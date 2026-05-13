from flask import Blueprint, render_template
from flask_login import login_required

from services.competition_service import WORLD_CUP_COMPETITION, ranking_rows_for_competition, recent_finished_predictions_by_user


ranking_bp = Blueprint("ranking", __name__)


@ranking_bp.route("/ranking")
@login_required
def ranking():
    rows = ranking_rows_for_competition(WORLD_CUP_COMPETITION)
    recent_predictions = recent_finished_predictions_by_user(WORLD_CUP_COMPETITION, [row[0].id for row in rows])
    return render_template(
        "ranking.html",
        rows=rows,
        recent_predictions=recent_predictions,
        page_title="Ranking Mundial",
        page_eyebrow="Tabla Mundial",
    )
