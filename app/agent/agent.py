import json
import os
from mistralai.client import Mistral
from dotenv import load_dotenv

from app.agent.agent_config import SYSTEM_PROMPT, TOOLS
from app.agent.tools.agent_tools import (
    get_all_customers,
    get_customer_overview,
    run_sql_query,
)
from app.services.analytics import (
    generate_statistical_analysis,
    generate_visual_analysis,
)

load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# Tool registry
TOOL_REGISTRY = {
    "get_all_customers": get_all_customers,
    "get_customer_overview": get_customer_overview,
    "run_sql_query": run_sql_query,
    "generate_statistical_analysis": generate_statistical_analysis,
    "generate_visual_analysis": generate_visual_analysis,
}


def run_agent(user_message: str, chat_history: list[dict]):
    """
    Clean, predictable, production-ready agent loop.
    """

    client = Mistral(api_key=MISTRAL_API_KEY)

    # Build message list
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(chat_history)
    messages.append({"role": "user", "content": user_message})

    # First model call
    response = client.chat.complete(
        model="mistral-medium-latest",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
        parallel_tool_calls=False,
    )

    assistant_message = response.choices[0].message
    messages.append(assistant_message.model_dump())

    # Tool loop
    while assistant_message.tool_calls:
        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name

            # Parse arguments safely
            try:
                args = json.loads(tool_call.function.arguments or "{}")
            except Exception:
                args = {}

            # Execute tool
            tool_fn = TOOL_REGISTRY.get(tool_name)
            if not tool_fn:
                result = {"error": f"Unknown tool: {tool_name}"}
            else:
                try:
                    result = tool_fn(**args)
                except Exception as exc:
                    result = {"error": str(exc)}

            # Append tool result
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result),
            })

        # Ask model again
        response = client.chat.complete(
            model="mistral-medium-latest",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            parallel_tool_calls=False,
        )

        assistant_message = response.choices[0].message
        messages.append(assistant_message.model_dump())

    # Final natural-language response
    return {
        "agent_response": assistant_message.content or "No response generated.",
        "history": messages,
    }
