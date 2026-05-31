from flask import Blueprint, request, session, jsonify
from app.agent.agent import run_agent

bp = Blueprint("api", __name__)

@bp.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message")

    # Retrieve history from session (Flask stores it securely)
    history = session.get("chat_history", [])

    # Run agent with history
    result = run_agent(user_message, history)

    tool = result.get("tool_result") or {}

    # Save updated history back into session
    session["chat_history"] = result["history"]

    return jsonify({
        "agent_response": result["agent_response"],
        "sql": tool.get("sql"),
        "rows": tool.get("rows"),
        "row_count": tool.get("row_count"),
        "history": result["history"]
    })



