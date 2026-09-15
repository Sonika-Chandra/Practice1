python
from flask import Blueprint, request, jsonify
from services.ai_service import analyze_assignment, generate_plan

# Create a Blueprint for AI routes
ai_controller = Blueprint("ai_controller", __name__)


@ai_controller.route("/analyze", methods=["POST"])
def analyze():
    try:
        # Get description from request body
        data = request.get_json()
        description = data.get("description")

        # Call AI service
        result = analyze_assignment(description)

        # Return result as JSON
        return jsonify(result), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500


@ai_controller.route("/plan", methods=["POST"])
def plan():
    try:
        # Get assignments from request body
        data = request.get_json()
        assignments = data.get("assignments")

        # Call AI service
        result = generate_plan(assignments)

        # Return result as JSON
        return jsonify(result), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500

