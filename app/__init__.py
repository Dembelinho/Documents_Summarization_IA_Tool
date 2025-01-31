from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        from . import routes
        # Create tables for our models
        db.create_all()

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    from app.routes import main
    app.register_blueprint(main)

    return app

