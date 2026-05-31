from flask import Flask, session
from flask_session import Session
from datetime import timedelta

from app.routes.api import bp as api_bp
from app.routes.home import home_bp as home_bp
from app.routes.db_test import db_test_bp

import logging
import os

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/sql_log.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

def create_app():
    app = Flask(__name__)

    # Secret key still required for signing session IDs
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret")

    # --- SERVER-SIDE SESSION STORAGE ---
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SESSION_FILE_DIR"] = "./flask_session"
    app.config["SESSION_PERMANENT"] = True
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=24)
    Session(app)
    # -----------------------------------

    # Register blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(db_test_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

