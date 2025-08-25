import os
from dotenv import load_dotenv

load_dotenv()


def env_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return str(val).strip().lower() in ("true", "True")


def env_str(name: str, default: str | None = None) -> str | None:
    return os.getenv(name, default)


class Config:
    SECRET_KEY = env_str("SECRET_KEY", "mysecret")
    SQLALCHEMY_DATABASE_URI = env_str("DATABASE_URI", "sqlite:///users.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = env_bool("SQLALCHEMY_TRACK_MODIFICATIONS", False)


class DevelopmentConfig(Config):
    DEBUG = env_bool("DEBUG", True)


class ProductionConfig(Config):
    DEBUG = env_bool("DEBUG", False)


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = env_str("TEST_DATABASE_URI", "sqlite:///:memory:")  # In-memory DB for testing
    SQLALCHEMY_TRACK_MODIFICATIONS = env_bool("SQLALCHEMY_TRACK_MODIFICATIONS", False)
    WTF_CSRF_ENABLED = env_bool("WTF_CSRF_ENABLED", False)  # Disable CSRF for easier testing
