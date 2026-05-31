from app.agent.agent import run_agent

TESTS = [
    ("Show me an overview of customer 1", "get_customer_overview"),
    ("List the accounts for customer 2", "get_customer_accounts"),
    ("How much money does customer 3 have?", "get_total_balance"),
    ("What is the total spend for customer 4?", "get_total_spend"),
    ("Show me monthly spend for customer 5", "get_monthly_spend"),
    ("Break down customer 6's spending by category", "get_spend_by_category"),
    ("What alerts does customer 7 have?", "get_customer_alerts"), 
    ("Give me the latest risk scores for customer 8", "get_customer_latest_risk"),
]

def run_tests():
    history = []

    for prompt, expected_tool in TESTS:
        print("\n----------------------------------------")
        print(f"USER: {prompt}")

        result = run_agent(prompt, history)
        history = result["history"]

        print("AGENT:", result["agent_response"])

        # Debug: print tool calls from history
        tool_messages = [m for m in history if m["role"] == "tool"]
        if tool_messages:
            print("TOOL CALL:", tool_messages[-1]["name"])
        else:
            print("TOOL CALL: None (unexpected)")

if __name__ == "__main__":
    run_tests()
