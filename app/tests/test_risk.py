from app.db.queries import execute_sql
from app.services.data_access import get_dataframe
from app.services.risk import (
    calculate_volatility,
    calculate_balance_trend,
    calculate_product_diversity,
    calculate_num_anomalies,
    extract_features,
    calculate_risk_score
)

# ---------------------------------------------------------
# 1. Run SQL for all required datasets
# ---------------------------------------------------------

tx_result = execute_sql("SELECT * FROM transactions LIMIT 100")
accounts_result = execute_sql("SELECT * FROM accounts LIMIT 100")
products_result = execute_sql("SELECT * FROM products LIMIT 100")
customer_products_result = execute_sql("SELECT * FROM customer_products LIMIT 100")

tx_df_name = tx_result["df_name"]
accounts_df_name = accounts_result["df_name"]
products_df_name = products_result["df_name"]
customer_products_df_name = customer_products_result["df_name"]

print("\n=== SQL Results ===")
print(tx_result)
print(accounts_result)
print(products_result)
print(customer_products_result)

# ---------------------------------------------------------
# 2. Load DataFrames
# ---------------------------------------------------------

transactions_df = get_dataframe(tx_df_name)
accounts_df = get_dataframe(accounts_df_name)
products_df = get_dataframe(products_df_name)
customer_products_df = get_dataframe(customer_products_df_name)

print("\n=== Loaded DataFrames ===")
print(transactions_df.head())
print(accounts_df.head())
print(products_df.head())
print(customer_products_df.head())

# ---------------------------------------------------------
# 3. Test risk.py
# ---------------------------------------------------------

print("\n=== Risk: Volatility ===")
print(calculate_volatility(tx_df_name))

print("\n=== Risk: Balance Trend ===")
print(calculate_balance_trend(tx_df_name, accounts_df_name))

print("\n=== Risk: Product Diversity ===")
print(calculate_product_diversity(customer_products_df_name, products_df_name))

print("\n=== Risk: Num Anomalies ===")
print(calculate_num_anomalies(tx_df_name))

print("\n=== Risk: Extract Features ===")
features = extract_features(
    tx_df_name,
    accounts_df_name,
    products_df_name,
    customer_products_df_name
)
print(features)

print("\n=== Risk: Full Risk Score ===")
score, contributions = calculate_risk_score(
    tx_df_name,
    accounts_df_name,
    products_df_name,
    customer_products_df_name
)
print("Score:", score)
print("Contributions:", contributions)
