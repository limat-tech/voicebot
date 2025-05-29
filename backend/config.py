import os
from dotenv import load_dotenv

load_dotenv() # Loads variables from .env file into environment variables

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-secret-dev-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://grocery_user:admin@localhost/grocery_voice_app'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
