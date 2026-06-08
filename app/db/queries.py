from app.db.connection import query
import logging
import re
from decimal import Decimal
from datetime import datetime, date
from app.services.analytics import register_sql_result

logger = logging.getLogger(__name__)

# -----------------------------
# SQL VALIDATION
# -----------------------------

def validate_sql(sql: str):
    forbidden = ["drop", "delete", "insert", "update", "alter", "truncate", "--"]

    lowered = sql.lower()

    for word in forbidden:
        pattern = r"\b" + re.escape(word) + r"\b"
        if re.search(pattern, lowered):
            return f"Forbidden SQL operation detected: {word}"

    # FIX: strip whitespace before checking semicolon position
    stripped = sql.strip()

    if ";" in stripped[:-1]:
        return "Multiple SQL statements are not allowed."

    return None

# -----------------------------
# RESULT CLEANING
# -----------------------------
def normalise_value(v):
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    return v


# -----------------------------
# SQL EXECUTION
# -----------------------------
def execute_sql(sql: str):
    """
    Execute the SQL query and return results as a list of dicts.
    """

    # 1. Validate SQL (guardrails)
    forbidden_sql = validate_sql(sql)

    if forbidden_sql:
        logger.warning(f"SQL validation failed: {forbidden_sql}")
        return {"error": forbidden_sql}

    logger.info(f"Executing SQL: {sql}")

    try:
        # 2. Execute the query
        rows, cursor = query(sql)
        columns = [desc[0] for desc in cursor.description]
        list_rows = [[normalise_value(v) for v in row] for row in rows]

        df_meta = register_sql_result(list_rows, columns)

       
        return {
            "status": "success",
            "sql": sql,
            **df_meta
        }

    except Exception as e:
        return {
            "status": "error",
            "sql": sql,
            "message": str(e)
        }