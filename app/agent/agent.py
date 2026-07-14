import json
import os
from mistralai.client import Mistral
from dotenv import load_dotenv

from app.services.explainability import log_event
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

from app.services.risk import (
    calculate_volatility,
    calculate_balance_trend,
    calculate_product_diversity,
    calculate_num_anomalies,
    calculate_risk_score
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
    "calculate_volatility": calculate_volatility,
    "calculate_balance_trend": calculate_balance_trend,
    "calculate_product_diversity": calculate_product_diversity,
    "calculate_num_anomalies": calculate_num_anomalies,
    "calculate_risk_score": calculate_risk_score
}

def run_agent(user_message: str, chat_history: list[dict]):

    reasoning_trace = []
    client = Mistral(api_key=MISTRAL_API_KEY)

    # Build message list
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(chat_history)
    messages.append({"role": "user", "content": user_message})

    #Track initial input
    reasoning_trace.append({
        "type": "user_input",
        "content": user_message
    })

    try:
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

        # Capture initial reasoning/thought process
        reasoning_trace.append({
            "type": "model_thought",
            "reasoning": getattr(assistant_message, "reasoning", None),
            "content": assistant_message.content
        })

        # Tool loop
        while assistant_message.tool_calls:
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name

                # Parse arguments safely
                try:
                    args = json.loads(tool_call.function.arguments or "{}")
                except Exception:
                    args = {}
                
                reasoning_trace.append({
                    "type": "tool_call",
                    "tool_name": tool_name,
                    "arguments": args
                })

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

            reasoning_trace.append({
                "type": "model_thought",
                "reasoning": getattr(assistant_message, "reasoning", None),
                "content": assistant_message.content
            })

        final_response = assistant_message.content or "No response generated."
        return {
            "agent_response": final_response,
            "history": messages 
        }

    except Exception as e:
        # Track the failure in the trace
        reasoning_trace.append({
            "type": "execution_failure", "error": str(e)
        })
        fallback_message = (
            "I apologise, but I encountered an unpected error while processing your request. "
            "Please try again in a moment, or contact support if the issue persists."
        )
        return {
            "agent_response": fallback_message,
            "history": messages
        }

    finally: 
        log_event("agent_conversation", {
            "user_message": user_message, 
            "assistant_response": assistant_message.content if 'assistant_message' in locals() else None
        })
        log_event("agent_reasoning_trace", {"trace": reasoning_trace})
