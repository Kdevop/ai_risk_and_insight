from app.db.queries import execute_sql
from app.services.data_access import get_dataframe
from app.services.analytics import generate_statistical_analysis, generate_visual_analysis

# ---------------------------------------------------------
# 1. Run SQL and register DataFrame
# ---------------------------------------------------------

sql_result = execute_sql("SELECT * FROM transactions LIMIT 100")
print("\n=== SQL Result ===")
print(sql_result)

df_name = sql_result["df_name"]

# ---------------------------------------------------------
# 2. Confirm DataFrame exists
# ---------------------------------------------------------

df = get_dataframe(df_name)
print("\n=== Loaded DataFrame Preview ===")
print(df.head())

# ---------------------------------------------------------
# 3. Test analytics.py
# ---------------------------------------------------------

print("\n=== Analytics: Summary Stats ===")
summary = generate_statistical_analysis(df_name, "summary_stats")
print(summary)

print("\n=== Analytics: Anomaly Detection ===")
anomalies = generate_statistical_analysis(
    df_name, 
    "anomaly_detection",
    column="amount"
    )
print(anomalies)

print("\n=== Analytics: Monthly Trend ===")
trend = generate_visual_analysis(
    df_name,
    "monthly_trend",
    date_column="timestamp",
    value_column="amount"
    )
print(trend)