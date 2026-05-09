import os


BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def _database_url():
    url = os.environ.get("DATABASE_URL")
    if url and url.startswith("postgres://"):
        return "postgresql+psycopg://" + url.removeprefix("postgres://")
    if url and url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url.removeprefix("postgresql://")
    return url or "sqlite:///" + os.path.join(BASE_DIR, "instance", "database.db")


def _is_enabled(value):
    return str(value).lower() in {"1", "true", "yes", "on"}


def _secret_key():
    secret_key = os.environ.get("SECRET_KEY")
    production = os.environ.get("FLASK_ENV") == "production" or os.environ.get("APP_ENV") == "production"
    if production and not secret_key:
        raise RuntimeError("SECRET_KEY es obligatoria en produccion.")
    return secret_key or "dev-secret-key-change-me"


class Config:
    SECRET_KEY = _secret_key()
    DEBUG = _is_enabled(os.environ.get("FLASK_DEBUG", "0"))
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
    APP_TIMEZONE = os.environ.get("APP_TIMEZONE", "America/Bogota")
    API_FOOTBALL_KEY = os.environ.get("API_FOOTBALL_KEY")
    API_FOOTBALL_BASE_URL = os.environ.get("API_FOOTBALL_BASE_URL", "https://v3.football.api-sports.io")
    WORLD_CUP_LEAGUE_ID = os.environ.get("WORLD_CUP_LEAGUE_ID")
    WORLD_CUP_SEASON = os.environ.get("WORLD_CUP_SEASON", "2026")
    LIGA_BETPLAY_LEAGUE_ID = os.environ.get("LIGA_BETPLAY_LEAGUE_ID")
    LIGA_BETPLAY_SEASON = os.environ.get("LIGA_BETPLAY_SEASON", "2026")
    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
