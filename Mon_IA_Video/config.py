import os
import secrets
from dotenv import load_dotenv

load_dotenv()

class Config:
    # SECRET_KEY is mandatory for security. If missing, generate a random one (for dev only, in prod it should fail).
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("ERREUR CRITIQUE: SECRET_KEY est manquant dans le fichier .env ! L'application ne peut pas démarrer en sécurité.")
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 1024 * 1024 * 500)) # 500MB max default instead of 5GB

    # Sécurité des Cookies
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
