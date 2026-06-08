# test_stats.py
from app.db.queries import execute_sql
from app.services.analytics import generate_statistical_analysis, get_dataframe

# 1. Run SQL
sql_result = execute_sql("SELECT * FROM transactions")
print(sql_result)

df_name = sql_result["df_name"]

# 2. Confirm DataFrame exists
df = get_dataframe(df_name)
print(df.head())

# 3. Run anomaly detection
stats = generate_statistical_analysis(
    df_name,
    "anomaly_detection",
    {
        "column": "amount",      # numeric column to scan
        "z_threshold": 3.0       # optional, defaults to 3.0
    }
)

print(stats)


