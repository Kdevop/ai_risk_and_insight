from flask import Blueprint, session, jsonify

clear_chat_bp = Blueprint("clear_chat", __name__)

@clear_chat_bp.route("/clear_chat", methods=["POST"])
def clear_chat():
    session.clear()
    return jsonify({"message": "Chat history cleared."})