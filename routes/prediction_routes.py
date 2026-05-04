from flask import Blueprint, flash, redirect, request, url_for
from flask_login import current_user, login_required

from models import db
from models.match import Match
from models.prediction import Prediction
from services.points_service import update_prediction_points


prediction_bp = Blueprint("prediction", __name__)


@prediction_bp.route("/predictions/<int:match_id>", methods=["POST"])
@login_required
def save_prediction(match_id):
    match = Match.query.get_or_404(match_id)
    if not match.can_predict:
        flash("Este partido ya comenzo. La prediccion esta bloqueada.", "error")
        return redirect(url_for("match.matches"))

    try:
        pred_home_score = int(request.form.get("pred_home_score", ""))
        pred_away_score = int(request.form.get("pred_away_score", ""))
    except ValueError:
        flash("Ingresa goles validos.", "error")
        return redirect(url_for("match.matches"))

    if pred_home_score < 0 or pred_away_score < 0:
        flash("Los goles no pueden ser negativos.", "error")
        return redirect(url_for("match.matches"))

    prediction = Prediction.query.filter_by(user_id=current_user.id, match_id=match.id).first()
    if prediction is None:
        prediction = Prediction(user_id=current_user.id, match=match)
        db.session.add(prediction)

    prediction.pred_home_score = pred_home_score
    prediction.pred_away_score = pred_away_score
    update_prediction_points(prediction)
    db.session.commit()

    flash("Prediccion guardada.", "success")
    return redirect(url_for("match.matches"))
