from app.db.queries import execute_sql

def agent_generated_query(user_input: str) -> str:
    """
    This function is a placeholder for the logic that would generate a SQL query based on user input.
    In a real implementation, this could involve an LLM or some other logic to convert natural language into SQL.
    For now, it simply returns a hardcoded query.
    """
    return "SELECT first_name, last_name FROM customers LIMIT 5;"


# 1. CUSTOMER OVERVIEW
def get_customer_overview(customer_id: int):
    sql = f"""
    SELECT 
        c.customer_id,
        c.first_name,
        c.last_name,
        c.email,
        c.phone,
        c.risk_tier,
        COUNT(a.account_id) AS account_count,
        SUM(a.balance) AS total_balance
    FROM customers c
    LEFT JOIN accounts a ON c.customer_id = a.customer_id
    WHERE c.customer_id = {customer_id}
    GROUP BY c.customer_id;
    """
    return execute_sql(sql)


# 2. CUSTOMER ACCOUNTS
def get_customer_accounts(customer_id: int):
    sql = f"""
    SELECT 
        account_id,
        account_type,
        balance,
        opened_at
    FROM accounts
    WHERE customer_id = {customer_id}
    ORDER BY opened_at DESC;
    """
    return execute_sql(sql)


# 3. TOTAL BALANCE
def get_total_balance(customer_id: int):
    sql = f"""
    SELECT 
        SUM(balance) AS total_balance
    FROM accounts
    WHERE customer_id = {customer_id};
    """
    return execute_sql(sql)


# 4. TOTAL SPEND
def get_total_spend(customer_id: int):
    sql = f"""
    SELECT 
        SUM(t.amount) AS total_spend
    FROM transactions t
    JOIN accounts a ON t.account_id = a.account_id
    WHERE a.customer_id = {customer_id};
    """
    return execute_sql(sql)


# 5. MONTHLY SPEND
def get_monthly_spend(customer_id: int):
    sql = f"""
    SELECT 
        TO_CHAR(t.timestamp, 'YYYY-MM') AS month,
        SUM(t.amount) AS total_spend
    FROM transactions t
    JOIN accounts a ON t.account_id = a.account_id
    WHERE a.customer_id = {customer_id}
    GROUP BY month
    ORDER BY month DESC
    LIMIT 12;
    """
    return execute_sql(sql)


# 6. SPEND BY CATEGORY
def get_spend_by_category(customer_id: int):
    sql = f"""
    SELECT 
        t.category,
        SUM(t.amount) AS total_spend
    FROM transactions t
    JOIN accounts a ON t.account_id = a.account_id
    WHERE a.customer_id = {customer_id}
    GROUP BY t.category
    ORDER BY total_spend DESC;
    """
    return execute_sql(sql)


# 7. CUSTOMER ALERTS
def get_customer_alerts(customer_id: int):
    sql = f"""
    SELECT 
        alert_id,
        alert_type,
        severity,
        created_at,
        resolved
    FROM alerts
    WHERE customer_id = {customer_id}
    ORDER BY created_at DESC;
    """
    return execute_sql(sql)


# 8. LATEST RISK SCORE
def get_customer_latest_risk(customer_id: int):
    sql = f"""
    SELECT 
        score_type,
        score,
        generated_at
    FROM risk_scores
    WHERE customer_id = {customer_id}
    ORDER BY generated_at DESC
    LIMIT 3;
    """
    return execute_sql(sql)

TOOL_REGISTRY = {
    "get_customer_overview": get_customer_overview,
    "get_customer_accounts": get_customer_accounts,
    "get_total_balance": get_total_balance,
    "get_total_spend": get_total_spend,
    "get_monthly_spend": get_monthly_spend,
    "get_spend_by_category": get_spend_by_category,
    "get_customer_alerts": get_customer_alerts,
    "get_customer_latest_risk": get_customer_latest_risk
}