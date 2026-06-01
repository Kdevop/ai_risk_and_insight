from app.db.queries import execute_sql
from app.services.analytics import generate_statistical_analysis, get_dataframe, generate_visual_analysis

# 1. Run SQL
sql_result = execute_sql("SELECT * FROM transactions")
print(sql_result)

df_name = sql_result["df_name"]

# 2. Confirm DataFrame exists
df = get_dataframe(df_name)
print(df.head())

# 3. Run visuals
print(generate_visual_analysis(
    df_name,
    "monthly_trend",
    {"date_column": "timestamp", "value_column": "amount"}
))

