from app.db.connection import query
import logging
from decimal import Decimal
from datetime import datetime, date

logger = logging.getLogger(__name__)

# -----------------------------
# SQL VALIDATION
# -----------------------------
import re

def validate_sql(sql: str):
    print(f"Validating SQL: {sql}")

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
def enforce_limit(sql: str, limit: int = 50):
    print(f"Enforcing LIMIT on SQL: {sql}")

    lowered = sql.lower()

    # If LIMIT already exists, do nothing
    if "limit" in lowered:
        return sql

    # Strip whitespace and trailing semicolon
    clean = sql.strip().rstrip(";")

    response = clean + f" LIMIT {limit};"
    print(f"SQL after enforcing LIMIT: {response}")

    # Append LIMIT safely
    return response


# -----------------------------
# RESULT CLEANING
# -----------------------------

def clean_results(rows):
    """
    Converts SQLAlchemy Row objects into JSON-safe dicts.
    Handles:
    - Decimal → float
    - datetime/date → ISO strings
    """

    cleaned = []

    if not rows:
        return {"row_count": 0, "rows": []}

    for row in rows:
        # SQLAlchemy Row → dict
        if hasattr(row, "_mapping"):
            data = dict(row._mapping)
        else:
            # fallback: treat as tuple with no column names
            # but this should never happen with SQLAlchemy
            data = dict(row)

        # Convert values
        for k, v in data.items():
            if isinstance(v, Decimal):
                data[k] = float(v)
            elif isinstance(v, (datetime, date)):
                data[k] = v.isoformat()

        cleaned.append(data)

    return {
        "row_count": len(cleaned),
        "rows": cleaned
    }

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
        rows = query(sql)

        # 4. Clean and structure results
        cleaned_results = clean_results(rows)

        return cleaned_results

    except Exception as e:
        logger.error(f"Error executing SQL: {e}")
        return {"error": str(e)}
