import os
import json
from typing import List, Optional
from dateutil import parser as date_parser
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# -------------------------------------------------------------
# 1. Environment & API Key Connection
# -------------------------------------------------------------
# Load environment variables from .env if present
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_gemini_client(api_key: Optional[str] = None) -> genai.Client:
    """Connects to Google GenAI with the configured API key."""
    key = api_key or GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ValueError(
            "GEMINI_API_KEY is not configured! Please set it in your .env file "
            "or as an environment variable (export GEMINI_API_KEY='...')."
        )
    return genai.Client(api_key=key)


# -------------------------------------------------------------
# 2. Flask Application Setup
# -------------------------------------------------------------
app = Flask(__name__)
# Enable CORS so your frontend (React/Vite or any client) can connect seamlessly
CORS(app)


# -------------------------------------------------------------
# 3. Pydantic Schemas for Gemini JSON Mode
# -------------------------------------------------------------
class AssignmentItem(BaseModel):
    subject: str = Field(description="Subject of the email")
    dueDate: Optional[str] = Field(default=None, description="Due date of assignment. Omit if not mentioned")
    isoDueDate: Optional[str] = Field(default=None, description="ISO or YYYY-MM-DD format for chronological sorting")
    summary: str = Field(description="Concise summary of the assignment")
    sender: Optional[str] = Field(default=None, description="Sender name or email address")


class ClubActivityItem(BaseModel):
    clubName: Optional[str] = Field(default=None, description="Name of the club. Omit if not mentioned")
    subject: str = Field(description="Subject of the email")
    summary: str = Field(description="Concise summary of the email body")
    registrationDate: Optional[str] = Field(default=None, description="Registration date/deadline. Omit if not mentioned")
    sender: Optional[str] = Field(default=None, description="Sender name or email address")


class ImportantDateItem(BaseModel):
    date: str = Field(description="The important date")
    natureOrDesc: str = Field(description="Few words about the date or its significance")


class ExamUpdateItem(BaseModel):
    subject: Optional[str] = Field(default=None, description="Subject of the email")
    summary: str = Field(description="Concise summary of exam updates")
    importantDates: Optional[List[ImportantDateItem]] = Field(default_factory=list, description="Important dates and their description")
    sender: Optional[str] = Field(default=None, description="Sender name or email address")


class DatedSegmentItem(BaseModel):
    subject: str = Field(description="Subject of the email")
    summary: str = Field(description="Concise summary of the activity/opportunity/announcement")
    importantDates: Optional[List[ImportantDateItem]] = Field(default_factory=list, description="Important dates along with nature")
    sender: Optional[str] = Field(default=None, description="Sender name or email address")


class PromotionSpamItem(BaseModel):
    subject: str = Field(description="Subject of the email")
    summary: str = Field(description="Very concise summary of the promotion or spam")
    sender: Optional[str] = Field(default=None, description="Sender name or email address")


class OrganizedEmailResponse(BaseModel):
    assignments: List[AssignmentItem] = Field(default_factory=list, description="Assignment emails sorted chronologically by due date")
    clubActivities: List[ClubActivityItem] = Field(default_factory=list, description="Club activities")
    examUpdates: List[ExamUpdateItem] = Field(default_factory=list, description="Exam updates")
    announcements: List[DatedSegmentItem] = Field(default_factory=list, description="Campus announcements")
    extraCurricularActivities: List[DatedSegmentItem] = Field(default_factory=list, description="Extra curricular activities")
    externalEduAndJobOpportunities: List[DatedSegmentItem] = Field(default_factory=list, description="External opportunities")
    competitions: List[DatedSegmentItem] = Field(default_factory=list, description="Competitions and challenges")
    promotionsAndSpams: List[PromotionSpamItem] = Field(default_factory=list, description="Promotions and spam")
    rawReportText: Optional[str] = Field(default=None, description="Clean formatted text summary")


# -------------------------------------------------------------
# 4. Prompt Builder & Sorting Helpers
# -------------------------------------------------------------
def parse_date_for_sort(date_str: Optional[str]) -> float:
    """Parses date strings to timestamps for chronological sorting."""
    if not date_str or date_str.strip().lower() in ("none", "unspecified", "n/a"):
        return float("inf")
    try:
        return date_parser.parse(date_str, fuzzy=True).timestamp()
    except Exception:
        return float("inf")


def build_prompt(emails: List[dict]) -> str:
    """Builds the instruction prompt containing the student emails."""
    formatted_emails = []
    for idx, mail in enumerate(emails, start=1):
        formatted_emails.append(
            f"--- EMAIL #{idx} ---\n"
            f"ID: {mail.get('id', f'email-{idx}')}\n"
            f"SENDER: {mail.get('sender', 'Unknown')}\n"
            f"SUBJECT: {mail.get('subject', 'No Subject')}\n"
            f"DATE: {mail.get('dateReceived', 'N/A')}\n"
            f"BODY:\n{mail.get('body', '')}\n"
            f"-------------------"
        )

    emails_block = "\n\n".join(formatted_emails)

    return f"""You are an AI agent that goes through student emails, sorts and organizes them.
Analyze the sender and content of each provided email and classify them into the 8 designated academic segments.

STRICT INSTRUCTIONS:
- You must return a clean, valid JSON object matching the requested schema.
- If there are NO emails under a particular segment, return an empty array [].
- If any required piece of information (such as due date, club name, registration date, etc.) is NOT present in an email, OMIT that field.

SEGMENT CLASSIFICATION RULES:
1. assignments:
   - Provide: subject, due date, concise summary of the assignment. (Omit due date if not mentioned).
   - CRITICAL: Sort all assignments in strict chronological order of due dates (earliest due date first; assignments without a due date at the end).
   - Include isoDueDate (YYYY-MM-DD) if parseable.
2. club activities:
   - Mention club name, subject, concise summary of the body, and registration date (omit if not mentioned).
3. exam updates:
   - Mention summary and important dates along with a few words about the date (natureOrDesc).
4. announcements:
   - Give subject, concise summary, and any important date along with its nature (omit date if not mentioned).
5. extra curricular activities:
   - Give subject, concise summary, and any important date along with its nature (omit date if not mentioned).
6. external educational and job opportunities:
   - Give subject, concise summary, and any important date along with its nature (omit date if not mentioned).
7. competitions:
   - Give subject, concise summary, and any important date along with its nature (omit date if not mentioned).
8. promotions and spams:
   - Just give subject and very concise summary.

EMAILS TO PROCESS:
{emails_block}"""


def organize_student_emails(emails: List[dict], api_key: Optional[str] = None) -> dict:
    """Core logic to invoke Gemini with JSON mode, sort assignments, and format output."""
    client = get_gemini_client(api_key)
    prompt = build_prompt(emails)

    # Candidate models with fallback
    models_to_try = ["gemini-2.5-flash", "gemini-3.8-flash", "gemini-3.6-flash"]
    response = None
    last_error = None

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=OrganizedEmailResponse,
                    temperature=0.1,
                ),
            )
            if response and response.text:
                break
        except Exception as e:
            last_error = e
            continue

    if not response or not response.text:
        raise last_error or RuntimeError("Failed to generate response from Gemini API.")

    raw_data = json.loads(response.text)
    organized = OrganizedEmailResponse.model_validate(raw_data)
    result = organized.model_dump(exclude_none=True)

    # Chronological sort for assignments
    if result.get("assignments"):
        result["assignments"].sort(
            key=lambda item: parse_date_for_sort(item.get("isoDueDate") or item.get("dueDate"))
        )

    # Replace empty segments with 'none'
    segment_keys = [
        "assignments",
        "clubActivities",
        "examUpdates",
        "announcements",
        "extraCurricularActivities",
        "externalEduAndJobOpportunities",
        "competitions",
        "promotionsAndSpams",
    ]

    for key in segment_keys:
        items = result.get(key)
        if not items or len(items) == 0:
            result[key] = "none"

    return result


# -------------------------------------------------------------
# 5. Flask API Routes
# -------------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint to verify Flask server and Gemini API key status."""
    has_key = bool(os.getenv("GEMINI_API_KEY") or GEMINI_API_KEY)
    return jsonify({
        "status": "ok",
        "framework": "Flask",
        "hasGeminiKey": has_key
    }), 200


@app.route("/api/organize-emails", methods=["POST"])
def api_organize_emails():
    """
    POST /api/organize-emails
    Payload: { "emails": [ { "id": "...", "sender": "...", "subject": "...", "body": "..." } ] }
    """
    try:
        data = request.get_json(force=True, silent=True)
        if not data or not isinstance(data.get("emails"), list):
            return jsonify({
                "error": "Invalid request body. Expected JSON object with an 'emails' list."
            }), 400

        emails = data["emails"]
        if len(emails) == 0:
            return jsonify({"error": "No emails provided in 'emails' list."}), 400

        # Run organization through Gemini
        organized_result = organize_student_emails(emails)
        return jsonify(organized_result), 200

    except ValueError as val_err:
        return jsonify({"error": str(val_err)}), 401
    except Exception as err:
        app.logger.error(f"Error processing emails: {err}")
        return jsonify({"error": f"Failed to organize emails: {str(err)}"}), 500


# -------------------------------------------------------------
# 6. Entry Point
# -------------------------------------------------------------
if __name__ == "__main__":
    # Checks for environment variable
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️ WARNING: GEMINI_API_KEY environment variable is not set.")
        print("Run: export GEMINI_API_KEY='your-key-here' or create a .env file.")
    else:
        print(" Connected to Gemini API Key.")

    port = int(os.getenv("PORT", 5000))
    print(f"🚀 Starting Flask server on http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
