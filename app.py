import os
import sys

from flask import Flask, render_template
from flask_migrate import Migrate
from flask_wtf import CSRFProtect

from config import Config
from data.matches_seed import seed_matches
from models import db, login_manager
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.api_results_routes import api_results_bp
from routes.liga_betplay_routes import liga_betplay_bp
from routes.match_routes import match_bp
from routes.prediction_routes import prediction_bp
from routes.ranking_routes import ranking_bp
from services.admin_service import ensure_admin_user
from services.schema_service import ensure_sqlite_schema
from services.team_flags import team_flag, team_flag_fallback
from services.time_service import format_local_datetime


csrf = CSRFProtect()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    csrf.exempt(api_results_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_results_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(liga_betplay_bp)
    app.register_blueprint(match_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(ranking_bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.context_processor
    def inject_team_helpers():
        return {"team_flag": team_flag, "team_flag_fallback": team_flag_fallback}

    app.jinja_env.filters["local_datetime"] = format_local_datetime

    if not is_migration_command():
        with app.app_context():
            db.create_all()
            if db.engine.name == "sqlite":
                ensure_sqlite_schema()
            ensure_admin_user(app.config.get("ADMIN_EMAIL"))
            seed_matches()

    return app


def is_migration_command():
    return "db" in sys.argv


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=app.config["DEBUG"])
