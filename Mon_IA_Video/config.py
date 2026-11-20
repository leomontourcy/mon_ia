import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # SECRET_KEY est obligatoire : l'application refuse de démarrer sans elle.
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("ERREUR CRITIQUE: SECRET_KEY est manquant dans le fichier .env ! L'application ne peut pas démarrer en sécurité.")
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 1024 * 1024 * 500))  # 500 Mo max par requête

    # Sécurité des Cookies
    # Cookies « Secure » (HTTPS) par défaut ; SESSION_COOKIE_SECURE=false uniquement en local sans HTTPS
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'true').lower() != 'false'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE
    REMEMBER_COOKIE_HTTPONLY = True
