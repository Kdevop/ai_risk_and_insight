from app.db.queries import execute_sql
from app.services.analytics import (
    get_dataframe,
    generate_visual_analysis
)

# 1. Run SQL
sql_result = execute_sql("SELECT * FROM transactions LIMIT 100")
print("\n=== SQL RESULT ===")
print(sql_result)

df_name = sql_result["df_name"]

# 2. Confirm DataFrame exists
df = get_dataframe(df_name)
print("\n=== DATAFRAME PREVIEW ===")
print(df.head())

# ---------------------------------------------------------
# TEST 1 — MONTHLY TREND
# ---------------------------------------------------------
print("\n=== TEST: monthly_trend ===")
monthly = generate_visual_analysis(
    df_name,
    "monthly_trend",
    date_column="timestamp",
    value_column="amount"
)
print(monthly)

# ---------------------------------------------------------
# TEST 2 — CATEGORY BREAKDOWN
# ---------------------------------------------------------
print("\n=== TEST: category_breakdown ===")
category = generate_visual_analysis(
    df_name,
    "category_breakdown",
    category_column="category",
    value_column="amount"
)
print(category)

# ---------------------------------------------------------
# TEST 3 — SCATTER PLOT
# ---------------------------------------------------------
print("\n=== TEST: scatter ===")
scatter = generate_visual_analysis(
    df_name,
    "scatter",
    x="transaction_id",
    y="amount"
)
print(scatter)

# ---------------------------------------------------------
# TEST 4 — REGRESSION PLOT
# ---------------------------------------------------------
print("\n=== TEST: regression ===")
regression = generate_visual_analysis(
    df_name,
    "regression",
    x="transaction_id",
    y="amount",
    degree=1
)
print(regression)
