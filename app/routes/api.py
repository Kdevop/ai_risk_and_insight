from flask import Blueprint, request, jsonify
import requests

bp = Blueprint("api", __name__)

FASTAPI_URL = "http://localhost:8000/agent"

@bp.route("/chat", methods=["POST"])
def chat():
    print("Received request into flask routes api.py:", request.json)

    data = request.get_json()
    user_message = data.get("message") if data else None

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    response = requests.post(
        FASTAPI_URL,
        json={"message": user_message}
    )

    return jsonify(response.json())


