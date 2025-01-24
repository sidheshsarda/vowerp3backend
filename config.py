from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Config:
    DEBUG = os.getenv("FLASK_DEBUG", "False") == "True"
    PORT = int(os.getenv("FLASK_PORT", 5003))
    HOST = "0.0.0.0"

    # Database configuration
    DB_HOST = os.getenv("DB_HOST")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
