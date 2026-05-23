from flask import Blueprint
import sqlalchemy
from app.db.connection import engine

db_test_bp = Blueprint("db_test", __name__)

@db_test_bp.route("/db-test")
def db_test():
    with engine.connect() as conn:
        result = conn.execute(sqlalchemy.text("SELECT NOW()")).fetchone()
    return f"Database time: {result[0]}"
