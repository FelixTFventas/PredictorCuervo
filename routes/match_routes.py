from sqlalchemy import func

from flask import Blueprint, render_template
from flask_login import current_user, login_required

from models.match import Match
from models.prediction import Prediction
from models.user import User


match_bp = Blueprint("match", __name__)


@match_bp.route("/dashboard")
@login_required
def dashboard():
    predictions = Prediction.query.filter_by(user_id=current_user.id).all()
    total_points = sum(prediction.points or 0 for prediction in predictions)
    exact_hits = sum(1 for prediction in predictions if prediction.points == 3)
    next_matches = Match.query.order_by(Match.starts_at.asc()).limit(3).all()

    ranking = (
        User.query.outerjoin(Prediction)
        .group_by(User.id)
        .order_by(func.coalesce(func.sum(Prediction.points), 0).desc(), User.username.asc())
        .all()
    )
    position = next((index + 1 for index, user in enumerate(ranking) if user.id == current_user.id), None)

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
    matches_list = Match.query.order_by(Match.starts_at.asc()).all()
    user_predictions = {
        prediction.match_id: prediction
        for prediction in Prediction.query.filter_by(user_id=current_user.id).all()
    }
    return render_template("matches.html", matches=matches_list, user_predictions=user_predictions)


@match_bp.route("/profile")
@login_required
def profile():
    predictions = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.updated_at.desc()).all()
    return render_template("profile.html", predictions=predictions)
