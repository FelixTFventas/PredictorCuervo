from flask import Blueprint, render_template
from flask_login import current_user, login_required

from models.match import Match
from models.prediction import Prediction
from services.competition_service import WORLD_CUP_COMPETITION, group_matches, ranking_rows_for_competition


match_bp = Blueprint("match", __name__)


@match_bp.route("/dashboard")
@login_required
def dashboard():
    predictions = Prediction.query.join(Match).filter(Prediction.user_id == current_user.id, Match.competition == WORLD_CUP_COMPETITION).all()
    total_points = sum(prediction.points or 0 for prediction in predictions)
    exact_hits = sum(1 for prediction in predictions if prediction.points == 3)
    next_matches = Match.query.filter_by(competition=WORLD_CUP_COMPETITION).order_by(Match.starts_at.asc()).limit(3).all()

    ranking = ranking_rows_for_competition(WORLD_CUP_COMPETITION)
    position = next((index + 1 for index, row in enumerate(ranking) if row[0].id == current_user.id), None)

    return render_template(
        "dashboard.html",
        predictions=predictions,
        total_points=total_points,
        exact_hits=exact_hits,
        next_matches=next_matches,
        position=position,
    )


@match_bp.route("/matches")
@login_required
def matches():
    matches_list = Match.query.filter_by(competition=WORLD_CUP_COMPETITION).order_by(Match.starts_at.asc()).all()
    grouped_matches = group_matches(matches_list)
    user_predictions = {
        prediction.match_id: prediction
        for prediction in Prediction.query.filter_by(user_id=current_user.id).all()
    }
    return render_template(
        "matches.html",
        grouped_matches=grouped_matches,
        user_predictions=user_predictions,
        page_title="Predicciones Mundial",
        page_description="Partidos del Mundial ordenados por grupos y fases. Los cruces pendientes se habilitan cuando tengan equipos definidos.",
        return_to="match.matches",
    )


@match_bp.route("/profile")
@login_required
def profile():
    predictions = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.updated_at.desc()).all()
    return render_template("profile.html", predictions=predictions)
