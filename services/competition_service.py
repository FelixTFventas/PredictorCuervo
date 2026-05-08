from collections import OrderedDict

from sqlalchemy import case, func

from models.match import Match
from models.prediction import Prediction
from models.user import User


WORLD_CUP_COMPETITION = "FIFA World Cup"
LIGA_BETPLAY_COMPETITION = "Liga BetPlay"
LIGA_BETPLAY_SEASON = "2026"


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
    total_points = func.coalesce(func.sum(case((Match.competition == competition, Prediction.points), else_=0)), 0)
    predictions_count = func.coalesce(func.sum(case((Match.competition == competition, 1), else_=0)), 0)
    exact_hits = func.coalesce(
        func.sum(case(((Match.competition == competition) & (Prediction.points == 3), 1), else_=0)),
        0,
    )

    return (
        User.query.outerjoin(Prediction, Prediction.user_id == User.id)
        .outerjoin(Match, Prediction.match_id == Match.id)
        .with_entities(User, total_points.label("total_points"), predictions_count.label("predictions_count"), exact_hits.label("exact_hits"))
        .group_by(User.id)
        .order_by(total_points.desc(), User.username.asc())
        .all()
    )
