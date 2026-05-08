from flask import Flask, render_template

from config import Config
from data.matches_seed import seed_matches
from models import db, login_manager
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.liga_betplay_routes import liga_betplay_bp
from routes.match_routes import match_bp
from routes.prediction_routes import prediction_bp
from routes.ranking_routes import ranking_bp
from services.admin_service import ensure_admin_user
from services.schema_service import ensure_sqlite_schema
from services.team_flags import team_flag, team_flag_fallback


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(admin_bp)
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

    with app.app_context():
        db.create_all()
        ensure_sqlite_schema()
        ensure_admin_user(app.config.get("ADMIN_EMAIL"))
        seed_matches()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
