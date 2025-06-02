"""
Main application package for the Grocery Voice App backend.

This module initializes the Flask application, extensions (SQLAlchemy, Migrate),
configures logging, and registers blueprints.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
import logging # <-- Add this import
import sys
from flask_jwt_extended import JWTManager

_logging_configured = False 

def configure_logging():
    global _logging_configured
    if not _logging_configured:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s',
            stream=sys.stdout # Explicitly log to stdout for console visibility
        )
        _logging_configured = True
# --- End Configure Logging ---

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_class=Config):
    """
    Create and configure an instance of the Flask application.

    This is the application factory function. It initializes extensions,
    registers blueprints, and sets up logging.

    Args:
        config_class (Config): The configuration class to use for the app.
                               Defaults to the Config class from config.py.

    Returns:
        Flask: The configured Flask application instance.
    """
    configure_logging()
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

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

    logger = logging.getLogger(__name__) # Get logger for app factory itself
    logger.info("Grocery Voice App created and configured.") # Example log at app creation

    return app
