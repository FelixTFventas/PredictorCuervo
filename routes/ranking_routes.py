from sqlalchemy import case, func

from flask import Blueprint, render_template
from flask_login import login_required

from models.prediction import Prediction
from models.user import User


ranking_bp = Blueprint("ranking", __name__)


@ranking_bp.route("/ranking")
@login_required
def ranking():
    rows = (
        User.query.outerjoin(Prediction)
        .with_entities(
            User,
            func.coalesce(func.sum(Prediction.points), 0).label("total_points"),
            func.count(Prediction.id).label("predictions_count"),
            func.coalesce(func.sum(case((Prediction.points == 3, 1), else_=0)), 0).label("exact_hits"),
        )
        .group_by(User.id)
        .order_by(func.coalesce(func.sum(Prediction.points), 0).desc(), User.username.asc())
        .all()
    )
    return render_template("ranking.html", rows=rows)
