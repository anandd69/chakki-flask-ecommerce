import os
from datetime import timedelta

class Config:
    # ── Security ──────────────────────────────────────────
    SECRET_KEY = os.environ.get('SECRET_KEY', 'chakki-secret-change-in-production-2026')
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

    # ── Database (Render PostgreSQL Compatible) ───────────
    DATABASE_URL = os.environ.get("DATABASE_URL")

    if DATABASE_URL:
        # Fix for Render postgres URL
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Local fallback (no MySQL required)
        SQLALCHEMY_DATABASE_URI = "sqlite:///local.db"

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