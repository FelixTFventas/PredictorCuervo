from flask import Blueprint, flash, jsonify, redirect, request, url_for
from flask_login import current_user, login_required

from models import db
from models.match import Match
from models.prediction import Prediction
from services.points_service import update_prediction_points


prediction_bp = Blueprint("prediction", __name__)

ALLOWED_RETURN_ENDPOINTS = {"match.matches", "liga_betplay.matches"}


def prediction_redirect():
    return_to = request.form.get("return_to", "match.matches")
    if return_to not in ALLOWED_RETURN_ENDPOINTS:
        return_to = "match.matches"
    return redirect(url_for(return_to))


def wants_json_response():
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def prediction_response(message, category="success", status_code=200, prediction=None):
    if wants_json_response():
        payload = {"message": message, "category": category}
        if prediction is not None:
            payload["prediction"] = {
                "home_score": prediction.pred_home_score,
                "away_score": prediction.pred_away_score,
                "points": prediction.points or 0,
            }
        return jsonify(payload), status_code

    flash(message, category)
    return prediction_redirect()


@prediction_bp.route("/predictions/<int:match_id>", methods=["POST"])
@login_required
def save_prediction(match_id):
    match = Match.query.get_or_404(match_id)
    if not match.can_predict:
        return prediction_response("Este partido ya comenzo. La prediccion esta bloqueada.", "error", 400)

    try:
        pred_home_score = int(request.form.get("pred_home_score", ""))
        pred_away_score = int(request.form.get("pred_away_score", ""))
    except ValueError:
        return prediction_response("Ingresa goles validos.", "error", 400)

    if pred_home_score < 0 or pred_away_score < 0:
        return prediction_response("Los goles no pueden ser negativos.", "error", 400)

    prediction = Prediction.query.filter_by(user_id=current_user.id, match_id=match.id).first()
    if prediction is None:
        prediction = Prediction(user_id=current_user.id, match=match)
        db.session.add(prediction)

    prediction.pred_home_score = pred_home_score
    prediction.pred_away_score = pred_away_score
    update_prediction_points(prediction)
    db.session.commit()

    return prediction_response("Prediccion guardada.", prediction=prediction)
