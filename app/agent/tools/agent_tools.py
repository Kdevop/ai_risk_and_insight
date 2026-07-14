from app.db.queries import execute_sql

# 1. GET ALL CUSTOMERS
def get_all_customers():
    print("Executing get_all_customers tool")
    sql = f"""
    SELECT 
        c.customer_id, 
        c.first_name, 
        c.last_name, 
        c.dob, c.email, 
        c.phone, 
        c.risk_tier 
    FROM customers c
    LIMIT 20;"""
  
    return execute_sql(sql)

# 2. CUSTOMER OVERVIEW
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

# 3. AGENT WRITEN CUSTOM SQL
def run_sql_query(query: str):
    return execute_sql(query) 

