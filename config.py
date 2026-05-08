import os


BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
    API_FOOTBALL_KEY = os.environ.get("API_FOOTBALL_KEY")
    API_FOOTBALL_BASE_URL = os.environ.get("API_FOOTBALL_BASE_URL", "https://v3.football.api-sports.io")
    WORLD_CUP_LEAGUE_ID = os.environ.get("WORLD_CUP_LEAGUE_ID")
    WORLD_CUP_SEASON = os.environ.get("WORLD_CUP_SEASON", "2026")
    LIGA_BETPLAY_LEAGUE_ID = os.environ.get("LIGA_BETPLAY_LEAGUE_ID")
    LIGA_BETPLAY_SEASON = os.environ.get("LIGA_BETPLAY_SEASON", "2026")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "instance", "database.db"),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
