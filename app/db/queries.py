from app.db.connection import query

def simple_query():
    rows = query("SELECT first_name, last_name FROM customers LIMIT 3;")
    return [dict(row._mapping) for row in rows]