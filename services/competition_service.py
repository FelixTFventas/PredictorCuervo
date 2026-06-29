from collections import OrderedDict

from sqlalchemy import case, func

from models import db
from models.champion_pick import ChampionPick
from models.match import Match
from models.prediction import Prediction
from models.user import User


WORLD_CUP_COMPETITION = "FIFA World Cup"
LIGA_BETPLAY_COMPETITION = "Liga BetPlay"
LIGA_BETPLAY_SEASON = "2026"
WORLD_CUP_VISIBLE_STAGES = {
    "Dieciseisavos",
    "Octavos de final",
    "Cuartos de final",
    "Semifinales",
    "Tercer puesto",
    "Final",
}


def world_cup_visible_stages_filter():
    return Match.stage.in_(WORLD_CUP_VISIBLE_STAGES)


def group_matches(matches):
    grouped = OrderedDict()
    for match in matches:
        if match.competition == LIGA_BETPLAY_COMPETITION:
            key = match.stage
        else:
            key = match.group_name if match.group_name != "Eliminacion directa" else match.stage
        grouped.setdefault(key, []).append(match)
    return grouped


def ranking_rows_for_competition(competition):
    match_points = func.coalesce(func.sum(case((Match.competition == competition, Prediction.points), else_=0)), 0)
    predictions_count = func.coalesce(func.sum(case((Match.competition == competition, 1), else_=0)), 0)
    exact_hit_condition = (
        (Match.competition == competition)
        & (Match.home_score.isnot(None))
        & (Match.away_score.isnot(None))
        & (Prediction.pred_home_score == Match.home_score)
        & (Prediction.pred_away_score == Match.away_score)
    )
    exact_hits = func.coalesce(func.sum(case((exact_hit_condition, 1), else_=0)), 0)
    query = User.query.outerjoin(Prediction, Prediction.user_id == User.id).outerjoin(Match, Prediction.match_id == Match.id)

    if competition == WORLD_CUP_COMPETITION:
        champion_points = (
            db.session.query(ChampionPick.user_id.label("user_id"), func.max(ChampionPick.points).label("points"))
            .group_by(ChampionPick.user_id)
            .subquery()
        )
        champion_bonus = func.coalesce(champion_points.c.points, 0)
        total_points = match_points + champion_bonus
        query = query.outerjoin(champion_points, champion_points.c.user_id == User.id)
        group_by_columns = [User.id, champion_points.c.points]
    else:
        total_points = match_points
        group_by_columns = [User.id]

    return (
        query
        .with_entities(User, total_points.label("total_points"), predictions_count.label("predictions_count"), exact_hits.label("exact_hits"))
        .group_by(*group_by_columns)
        .order_by(total_points.desc(), User.username.asc())
        .all()
    )


def recent_finished_predictions_by_user(competition, user_ids, limit=4):
    recent_predictions = {}
    for user_id in user_ids:
        predictions = (
            Prediction.query.join(Match)
            .filter(
                Prediction.user_id == user_id,
                Match.competition == competition,
                Match.home_score.isnot(None),
                Match.away_score.isnot(None),
            )
            .order_by(Match.starts_at.desc())
            .limit(limit)
            .all()
        )
        recent_predictions[user_id] = [
            {
                "teams": f"{prediction.match.home_team} vs {prediction.match.away_team}",
                "prediction": f"{prediction.pred_home_score} - {prediction.pred_away_score}",
                "result": f"{prediction.match.home_score} - {prediction.match.away_score}",
                "points": prediction.points or 0,
            }
            for prediction in predictions
        ]
    return recent_predictions
