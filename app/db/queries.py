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
# LIMIT ENFORCEMENT
# -----------------------------
def enforce_limit(sql: str, limit: int = 20):
    lowered = sql.lower()

    # If LIMIT already exists, do nothing
    if "limit" in lowered:
        return sql

    # Strip whitespace and trailing semicolon
    clean = sql.strip().rstrip(";")

    response = clean + f" LIMIT {limit};"

    # Append LIMIT safely
    return response

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

    # 2. Enforce LIMIT to avoid huge datasets (TOKEN CONTROL)
    sql = enforce_limit(sql)

    logger.info(f"Executing SQL: {sql}")

    try:
        # 3. Execute the query
        rows, cursor = query(sql)
        columns = [desc[0] for desc in cursor.description]
        list_rows = [[normalise_value(v) for v in row] for row in rows]

        df_meta = register_sql_result(list_rows, columns)

        # return {
        #     "sql": sql,
        #     "columns": columns,
        #     "rows": list_rows,
        #     "row_count": len(list_rows)
        # }
        
        return {
            "status": "success",
            "sql": sql,
            **df_meta
        }

    # except Exception as e:
    #     logger.error(f"Error executing SQL: {e}")
    #     return {"error": str(e)}
    except Exception as e:
        return {
            "status": "error",
            "sql": sql,
            "message": str(e)
        }