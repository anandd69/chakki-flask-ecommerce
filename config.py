import os
from datetime import timedelta

class Config:
    # ── Security ──────────────────────────────────────────
    SECRET_KEY = os.environ.get('SECRET_KEY', 'chakki-secret-change-in-production-2026')
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

    # ── Database ──────────────────────────────────────────
    DB_HOST     = os.environ.get('DB_HOST', 'localhost')
    DB_PORT     = int(os.environ.get('DB_PORT', 3306))
    DB_USER     = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME     = os.environ.get('DB_NAME', 'chakki_db')

    # SQLAlchemy URI
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        "?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 299,
        'pool_pre_ping': True,
    }

    # ── Session ───────────────────────────────────────────
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # ── App Settings ──────────────────────────────────────
    FREE_DELIVERY_ABOVE = 500
    DELIVERY_CHARGE     = 60
    ORDER_PREFIX        = 'CP'

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True

config = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'default':     DevelopmentConfig,
}