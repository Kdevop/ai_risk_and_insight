import json
import os
from dotenv import load_dotenv
from mistralai.client import Mistral

from app.services.explainability import log_event
from app.agent.agent_config import SYSTEM_PROMPT, TOOLS
from app.agent.tools.agent_tools import TOOL_REGISTRY

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")


# ---------------------------------------------------------
# Base message helpers
# ---------------------------------------------------------
def build_base_messages():
    return [{"role": "system", "content": SYSTEM_PROMPT}]


def add_user_message(messages, content: str):
    messages.append({"role": "user", "content": content})
    return messages


# ---------------------------------------------------------
# JSON-safe history conversion
# ---------------------------------------------------------
def to_json_safe_messages(messages):
    """
    Ensures all messages are JSON-serializable.
    Removes SDK objects (ToolCall, FunctionCall).
    """
    safe = []

    for m in messages:
        msg = {
            "role": m.get("role"),
            "content": m.get("content"),
        }

        # tool_calls 
        if "tool_calls" in m:
            msg["tool_calls"] = m["tool_calls"]

        # tool_call_id for tool result messages
        if "tool_call_id" in m:
            msg["tool_call_id"] = m["tool_call_id"]

        safe.append(msg)

    return safe


# ---------------------------------------------------------
# Model call
# ---------------------------------------------------------
def call_model(messages):
    client = Mistral(api_key=MISTRAL_API_KEY)

    return client.chat.complete(
        model="mistral-medium-latest",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
        parallel_tool_calls=False
    )


# ---------------------------------------------------------
# Tool call handling
# ---------------------------------------------------------
def handle_tool_calls(response, messages):
    message = response.choices[0].message

    # No tool calls → normal assistant message
    if not getattr(message, "tool_calls", None):
        messages.append({"role": "assistant", "content": message.content})
        return message.content, messages

    # Convert tool calls to JSON-safe dicts
    safe_tool_calls = []
    for tc in message.tool_calls:
        safe_tool_calls.append({
            "id": tc.id,
            "function": {
                "name": tc.function.name,
                "arguments": tc.function.arguments
            }
        })

    # Append assistant message containing tool calls
    messages.append({
        "role": "assistant",
        "content": message.content,
        "tool_calls": safe_tool_calls
    })

    # Execute each tool call
    for tc in message.tool_calls:
        tool_name = tc.function.name
        tool_args = json.loads(tc.function.arguments or "{}")

        tool_fn = TOOL_REGISTRY.get(tool_name)

        if not tool_fn:
            tool_result = {"error": f"Unknown tool: {tool_name}"}
        else:
            tool_result = tool_fn(**tool_args)

        # If tool returned an error → return directly
        if isinstance(tool_result, dict) and "error" in tool_result:
            error_msg = f"Tool `{tool_name}` failed: {tool_result['error']}"
            messages.append({"role": "assistant", "content": error_msg})
            return error_msg, messages

        # Append tool result with correct tool_call_id
        messages.append({
            "role": "tool",
            "tool_call_id": tc.id,
            "content": json.dumps(tool_result)
        })

    # Follow-up call so model can use tool results
    client = Mistral(api_key=MISTRAL_API_KEY)
    followup = client.chat.complete(
        model="mistral-medium-latest",
        messages=messages
    )

    print(f"Follow-up message: {followup.choices[0]}")

    final_message = followup.choices[0].message
    messages.append({"role": "assistant", "content": final_message.content})

    return final_message.content, messages


# ---------------------------------------------------------
# Main agent entrypoint
# ---------------------------------------------------------
def run_agent(user_input: str, history: list | None = None):
    """
    Main function called by the UI/backend.
    Handles:
    - chat history
    - tool-enabled model calls
    - tool execution
    - logging
    """

    # 1. Build or extend message history
    if not history:
        messages = build_base_messages()
    else:
        messages = history[:]

        # Ensure system prompt is always present
        if messages[0]["role"] != "system":
            messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

    # Remove incomplete tool calls
    if messages:
        last = messages[-1]
        if last.get("role") == "assistant" and "tool_calls" in last:
            messages = messages[:-1]

    add_user_message(messages, user_input)

    # 2. First model call
    response = call_model(messages)

    # 3. Handle tool calls + follow-up model call
    answer, updated_messages = handle_tool_calls(response, messages)

    # 4. Log for explainability
    log_event(user_input, answer)

    # 5. Return structured response with JSON-safe history
    return {
        "user_question": user_input,
        "agent_response": answer,
        "history": to_json_safe_messages(updated_messages)
    }


    # return {
    #     "user_question": user_input,
    #     "agent_response": answer.agent_response,
    #     "executed_sql": answer.executed_sql if hasattr(answer, "executed_sql") else None,
    #     "history": to_json_safe_messages(updated_messages)
    # }

