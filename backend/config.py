"""
Configuration settings for the Flask application.

Loads environment variables from a .env file and defines configuration
classes for different environments (though only a base Config is used here).
"""
import os
from dotenv import load_dotenv

load_dotenv() # Loads variables from .env file into environment variables

class Config:
    """
    Base configuration class.

    Contains default settings and loads sensitive information from
    environment variables.
    """
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')