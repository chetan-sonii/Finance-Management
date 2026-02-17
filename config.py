# app/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-dev-key")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+mysqlconnector://"
        f"{os.getenv('DB_USER')}:"
        f"{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:"
        f"{os.getenv('DB_PORT')}/"
        f"{os.getenv('DB_NAME')}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads
    AVATAR_UPLOAD_FOLDER = os.path.join(
        BASE_DIR,"1", "app", "static", "uploads", "avatars"
    )
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
