from flask import Blueprint, render_template
from flask_login import current_user, login_required

from models.match import Match
from models.prediction import Prediction
from services.competition_service import LIGA_BETPLAY_COMPETITION, LIGA_BETPLAY_SEASON, group_matches, ranking_rows_for_competition


liga_betplay_bp = Blueprint("liga_betplay", __name__, url_prefix="/liga-betplay")


@liga_betplay_bp.route("/")
@login_required
def index():
    matches_count = Match.query.filter_by(competition=LIGA_BETPLAY_COMPETITION, season=LIGA_BETPLAY_SEASON).count()
    finished_count = Match.query.filter_by(competition=LIGA_BETPLAY_COMPETITION, season=LIGA_BETPLAY_SEASON, status="finished").count()
    next_match = (
        Match.query.filter_by(competition=LIGA_BETPLAY_COMPETITION, season=LIGA_BETPLAY_SEASON)
        .order_by(Match.starts_at.asc())
        .first()
    )
    return render_template(
        "liga_betplay/index.html",
        matches_count=matches_count,
        finished_count=finished_count,
        next_match=next_match,
    )


@liga_betplay_bp.route("/matches")
@login_required
def matches():
    matches_list = (
        Match.query.filter_by(competition=LIGA_BETPLAY_COMPETITION, season=LIGA_BETPLAY_SEASON)
        .order_by(Match.starts_at.asc())
        .all()
    )
    user_predictions = {
        prediction.match_id: prediction
        for prediction in Prediction.query.join(Match).filter(
            Prediction.user_id == current_user.id,
            Match.competition == LIGA_BETPLAY_COMPETITION,
            Match.season == LIGA_BETPLAY_SEASON,
        )
    }
    return render_template(
        "liga_betplay/matches.html",
        grouped_matches=group_matches(matches_list),
        user_predictions=user_predictions,
        return_to="liga_betplay.matches",
    )


@liga_betplay_bp.route("/ranking")
@login_required
def ranking():
    rows = ranking_rows_for_competition(LIGA_BETPLAY_COMPETITION)
    return render_template(
        "ranking.html",
        rows=rows,
        page_title="Ranking Liga BetPlay",
        page_eyebrow="Tabla Liga BetPlay",
    )
