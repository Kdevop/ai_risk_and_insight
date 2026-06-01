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
    reasoning_trace = [] 

    # Remove ALL old system prompts to avoid duplication
    messages = [m for m in messages if m.get("role") != "system"]

    # Trip down oversized past payloads so they don't break context budget
    for m in messages:
        if m.get("role") == "tool":
            content = m.get("content", "")
            if isinstance(content, str) and len(content) > 1200:
                m["content"] = (
                    content[:1200]
                    + "... [truncated to preserve context window] ..."
                )


    # 2. Turn-aware history trimming
    MAX_HISTORY = 16
    if len(messages) > MAX_HISTORY:
        slice_index = len(messages) - MAX_HISTORY

        # Ensure we don't seperate a tools response from is assistant parent
        while slice_index > 0 and messages[slice_index].get("role") == "tool":
            slice_index -= 1

        #Ensure we don;t start right on an assistant tool definition block
        if slice_index > 0 and messages[slice_index].get("role") == "assistant" and "tool_calls" in messages[slice_index]:
            slice_index -= 1

        messages = messages[slice_index:]

    #Add the system prompt and user query
    messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
    messages.append({"role": "user", "content": user_input})

    # DEBUG: Print the full prompt sent to the model
    print("\n================ MODEL PROMPT ================")
    for m in messages:
        role = m.get("role")
        content = m.get("content")
        print(f"\n[{role.upper()}]\n{content}\n")
    print("==============================================\n")

    # 3. Multi-step agent execution loop
    MAX_ITERATIONS = 8
    iterations = 0

    while iterations < MAX_ITERATIONS:
        iterations += 1

        # Call the model with current context
        response = call_model(messages)
        msg = response.choices[0].message

        # Capture and log reasoning weights
        if hasattr(msg, "reasoning") and msg.reasoning:
            reasoning_trace.append({
                "type": "model_reasoning",
                "reasoning": msg.reasoning
            })
        elif msg.content:
            reasoning_trace.append({"type": "model_reasoning", "content": msg.content})

        # Route A: Model Request Tool Calls
        if getattr(msg, "tool_calls", None):
            safe_tool_calls = []
            tool_names = []

            for tc in msg.tool_calls:
                tool_names.append(tc.function.name)
                safe_tool_calls.append({
                    "id": tc.id,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                })

            # Force narrative anchor
            history_text = f"Thought: I need to fetch the relevant data. Executing tools: {', '.join(tool_names)}"

            # Commit the Assistant intent safely to the historical timeline
            messages.append({
                "role": "assistant",
                "content": history_text,
                "tool_calls": safe_tool_calls
            })

            # Execute the parallel/sebquenced tools array
            for tc in msg.tool_calls:
                tool_name = tc.function.name
                reasoning_trace.append({
                    "type": "tool_selected",
                    "tool": tool_name,
                    "arguments": tc.function.arguments
                })

                # Robust Argument Extraction
                if isinstance(tc.function.arguments, dict):
                    tool_args = tc.function.arguments
                else:
                    try:
                        tool_args = json.loads(tc.function.arguments or "{}")
                    except Exception:
                        tool_args = {}

                # Execute call again system registry
                tool_fn = TOOL_REGISTRY.get(tool_name)
                if not tool_fn:
                    result = {"error": f"Tool {tool_name} not found."}
                else:
                    try:
                        result = retry(lambda: tool_fn(**tool_args))
                        if tool_name == "run_sql_query":
                            reasoning_trace.append({
                                "type": "sql_executed",
                                "sql": tool_args.get("sql", "")
                            })

                    except Exception as exc:
                        result = {"error": f"Execution failed on tool side: {str(exc)}"}

                print(f"Tool '{tool_name}' executed with result: {result}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result)
                })

            # Loop back to evaluation pass woth tool data
            continue

        # Route B: No tool calls, final response ready
        messages.append({
            "role": "assistant",
            "content": msg.content
        })

        reasoning_trace.append({
            "type": "agent_response",
            "content": msg.content
        })

        #Logs for explainability 
        log_event(user_input, msg.content)
        log_event("reasoning_trace", reasoning_trace)

        return {
            "agent_response": msg.content,
            "history": to_json_safe_messages(messages),
        }


    # Emergency escape hatch
    error_fallback = (
        "I encountered an optimisation bottleneck processing your multi-step "
        "analytics sequence. Please narrow your query parameters."
    )

    messages.append({
        "role": "assistant",
        "content": error_fallback
    })

    reasoning_trace.append({
        "type": "agent_response",
        "content": error_fallback
    })

    log_event(user_input, msg.content)
    log_event("reasoning_trace", reasoning_trace)

    return {
        "agent_response": error_fallback,
        "history": to_json_safe_messages(messages)
    }