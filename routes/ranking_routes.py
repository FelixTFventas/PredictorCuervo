from flask import Blueprint, render_template
from flask_login import login_required

from services.competition_service import WORLD_CUP_COMPETITION, ranking_rows_for_competition


ranking_bp = Blueprint("ranking", __name__)


@ranking_bp.route("/ranking")
@login_required
def ranking():
    rows = ranking_rows_for_competition(WORLD_CUP_COMPETITION)
    return render_template("ranking.html", rows=rows, page_title="Ranking Mundial", page_eyebrow="Tabla Mundial")
