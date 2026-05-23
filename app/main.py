from flask import Flask
from app.routes.home import home_bp
from app.routes.db_test import db_test_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(home_bp)
    app.register_blueprint(db_test_bp)   
    return app


app = create_app()