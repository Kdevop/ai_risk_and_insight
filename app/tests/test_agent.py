from app.agent.agent import run_agent

def run_scenario(name, prompt):
    print(f"\n\n================= SCENARIO: {name} =================\n")
    response = run_agent(prompt)
    print("\n--- RAW AGENT JSON RESPONSE ---\n")
    print(response)


def test_agent_multi():
    # 1. Basic SQL query
    # run_scenario(
    #     "SQL Query",
    #     "Run SQL: SELECT * FROM transactions LIMIT 20;"
    # )

    # # # 2. Summary statistics
    # run_scenario(
    #     "Summary Stats",
    #     "Give me summary statistics for the amount column in transactions."
    # )

    # 3. Correlation
    # run_scenario(
    #     "Correlation",
    #     "Find the correlation between amount and transaction_id."
    # )

    # 4. Anomaly detection
    # run_scenario(
    #     "Anomaly Detection",
    #     "Detect anomalies in the amount column in transactions using z-score."
    # )

    # # 5. Monthly trend visual
    # run_scenario(
    #     "Monthly Trend",
    #     "Plot the monthly trend of transaction amounts for the past 12 months."
    # )

    # # 6. Category breakdown visual
    # run_scenario(
    #     "Category Breakdown",
    #     "Show a category breakdown of spending over the past 12 months."
    # )

    # 7. Scatter plot
    run_scenario(
        "Scatter Plot",
        "Create a scatter plot of transaction amount over time."
    )

    # 8. Regression plot
    run_scenario(
        "Regression Plot",
        "Run a regression of transaction amount against account balance."
    )

    # 9. Customer lookup
    # run_scenario(
    #     "Customer Overview",
    #     "Show me an overview for customer 1."
    # )

    # 10. Free-text natural language query
    # run_scenario(
    #     "Free Text Reasoning",
    #     "What insights can you find about spending patterns in this dataset?"
    # )


if __name__ == "__main__":
    test_agent_multi()
