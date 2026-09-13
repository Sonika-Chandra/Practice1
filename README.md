# Gmail Assignment Agent (Practice Project)

A practice build for the Craft N Code hackathon (AI for Education theme). This project reads a user's Gmail inbox, identifies assignment/deadline-related emails, and (eventually) uses AI to categorize and prioritize them, adding relevant deadlines to Google Calendar.

## Status
🚧 Practice/prototype — built ahead of the actual hackathon to learn the OAuth + Gmail API + AI integration pattern before problem statements are released.

## What's working so far
- **`gmail_parser.py`** — parses a raw Gmail API message object into a clean dictionary (subject, sender, date, body)
- **`gmail_service.py`** — fetches message IDs from Gmail (`list_message_ids`) and retrieves full message details for each (`fetch_full_messages`)
- **`app.py`** — a Flask route (`/fetch-emails`) that chains the above together and returns results as JSON

## What's not built yet
- Google OAuth login flow (in progress — separate teammate)
- AI categorization of emails using Gemini (in progress — separate teammate)
- Frontend to display results (in progress — separate teammate)
- Google Calendar integration to add deadlines automatically

## Tech stack
- Backend: Python, Flask
- APIs: Gmail API (Calendar/Classroom planned)
- AI: Google Gemini (planned)
- Frontend: HTML/CSS/JS with Tailwind (planned)

## Setup
1. Clone the repo
2. `cd backend`
3. Create and activate a virtual environment:
    python -m venv venv
    venv\Scripts\activate # Windows
    source venv/bin/activate # Mac/Linux
4. Install dependencies: `pip install flask google-api-python-client google-auth google-auth-oauthlib`
5. Add a `.env` file with your Gmail OAuth credentials (see `.env.example` if provided)
6. Run: `python app.py`

## Team / Roles
- Role A: Google OAuth setup
- Role B: Gmail data fetching (this practice build)
- Role C: AI logic (Gemini prompting)
- Role D: Frontend
