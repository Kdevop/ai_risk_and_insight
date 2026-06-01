from app.db.queries import execute_sql
from app.services.analytics import get_dataframe

result = execute_sql("SELECT * FROM transactions")
print(result)

df_name = result["df_name"]
df = get_dataframe(df_name)
print(df.head())
