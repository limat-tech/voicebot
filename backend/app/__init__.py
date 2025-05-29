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

    # Blueprints will be registered here later
    # from .routes.auth import auth_bp
    # app.register_blueprint(auth_bp)

    # from .routes.products import products_bp
    # app.register_blueprint(products_bp)
    from app import models
    return app
