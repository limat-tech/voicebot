# backend/app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    # --- Import and Register Blueprints ---
    # Import your blueprint objects here
    from app.routes.auth import auth_bp
    from app.routes.products import products_bp

    # Register the blueprints with the Flask app instance
    # This makes all routes defined in auth_bp and products_bp active
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    # --- End Blueprint Registration ---

    # This line helps discover models for Flask-Migrate and other extensions
    # Ensure it's placed where it can "see" the model definitions
    from app import models # If models are in app/models/__init__.py

    return app
