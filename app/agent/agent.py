import json
import os
import time
from dotenv import load_dotenv
from mistralai.client import Mistral

from app.services.explainability import log_event
from app.agent.agent_config import SYSTEM_PROMPT, TOOLS
from app.agent.tools.agent_tools import TOOL_REGISTRY

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")


# ---------------------------------------------------------
# Retry helper (for model + sql)
# ---------------------------------------------------------
def retry(fn, retries=3, delay=0.2):
    for i in range(retries):
        try:
            return fn()
        except Exception:
            if i == retries - 1:
                raise
            time.sleep(delay)


# ---------------------------------------------------------
# JSON-safe history conversion
# ---------------------------------------------------------
def to_json_safe_messages(messages):
    safe = []
    for m in messages:
        msg = {
            "role": m.get("role"),
            "content": m.get("content"),
        }
        if "tool_calls" in m:
            msg["tool_calls"] = m["tool_calls"]
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
# Main agent entrypoint
# ---------------------------------------------------------
def run_agent(user_input: str, history: list | None = None):

    # 1. Build or extend message history safely
    messages = history[:] if history else []

    # Remove ALL old system prompts to avoid duplication
    messages = [m for m in messages if m.get("role") != "system"]

    # ---------------------------------------------------------
    # PERFORMANCE FIX 1: Aggressive cleaning of tool outputs
    # ---------------------------------------------------------
    for m in messages:
        if m.get("role") == "tool":
            content = m.get("content", "")
            if isinstance(content, str) and len(content) > 1200:
                m["content"] = (
                    content[:1200]
                    + "... [truncated to preserve context window] ..."
                )

    # ---------------------------------------------------------
    # Insert fresh system prompt at the top
    # ---------------------------------------------------------
    messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

    # ---------------------------------------------------------
    # PERFORMANCE FIX 2: System prompt anchor reminder
    # ---------------------------------------------------------
    messages.append({
        "role": "system",
        "content": (
            "REMINDER: You are a Banking Analytics Assistant. "
            "You MUST use predefined tools first. "
            "Use SQL ONLY when tools cannot answer the question. "
            "Never claim you lack capabilities."
        )
    })

    # ---------------------------------------------------------
    # Trim history safely (Keep system instructions intact)
    # ---------------------------------------------------------
    MAX_HISTORY = 16
    if len(messages) > MAX_HISTORY + 1:
        trimmed = [messages[0]] + messages[-MAX_HISTORY:]

        # Ensure we did NOT cut a tool_call → tool_result pair
        if trimmed[-1].get("role") == "assistant" and "tool_calls" in trimmed[-1]:
            trimmed = trimmed[:-1]

        messages = trimmed

    # 2. Append the fresh user challenge
    messages.append({"role": "user", "content": user_input})

    # 3. Request initial routing from the model
    response = call_model(messages)
    msg = response.choices[0].message

    # ---------------------------------------------------------
    # Safe Multi-step loop with iteration limits
    # ---------------------------------------------------------
    MAX_ITERATIONS = 8
    iterations = 0

    while iterations < MAX_ITERATIONS:
        iterations += 1

        # -----------------------------------------------------
        # CASE 1: Model requests Tool Executions
        # -----------------------------------------------------
        if getattr(msg, "tool_calls", None):

            safe_tool_calls = []
            for tc in msg.tool_calls:
                safe_tool_calls.append({
                    "id": tc.id,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                })

            # Commit the Assistant intent safely to the historical timeline
            messages.append({
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": safe_tool_calls
            })

            # Execute matching sub-tools sequentially
            for tc in msg.tool_calls:
                tool_name = tc.function.name

                # Robust Argument Extraction
                if isinstance(tc.function.arguments, dict):
                    tool_args = tc.function.arguments
                else:
                    try:
                        tool_args = json.loads(tc.function.arguments or "{}")
                    except Exception:
                        tool_args = {}

                tool_fn = TOOL_REGISTRY.get(tool_name)
                if not tool_fn:
                    result = {"error": f"Tool {tool_name} not found."}
                else:
                    try:
                        result = retry(lambda: tool_fn(**tool_args))
                    except Exception as exc:
                        result = {"error": f"Execution failed on tool side: {str(exc)}"}

                print(f"Tool '{tool_name}' executed with result: {result}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result)
                })

            # Re-query the model with updated context
            response = call_model(messages)
            msg = response.choices[0].message
            continue

        # -----------------------------------------------------
        # CASE 2: Final synthesized resolution achieved
        # -----------------------------------------------------
        messages.append({
            "role": "assistant",
            "content": msg.content
        })

        log_event(user_input, msg.content)

        return {
            "agent_response": msg.content,
            "history": to_json_safe_messages(messages)
        }

    # Emergency escape hatch
    error_fallback = (
        "I encountered an optimization bottleneck processing your multi-step "
        "analytics sequence. Please narrow your query parameters."
    )

    messages.append({
        "role": "assistant",
        "content": error_fallback
    })

    return {
        "agent_response": error_fallback,
        "history": to_json_safe_messages(messages)
    }