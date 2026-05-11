from urllib.parse import urlparse

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from models import db
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


def _is_valid_avatar_url(avatar_url):
    if not avatar_url:
        return True
    parsed = urlparse(avatar_url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


@match_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        form_action = request.form.get("form_action")

        if form_action == "profile":
            display_name = request.form.get("display_name", "").strip()
            avatar_url = request.form.get("avatar_url", "").strip()

            if len(display_name) > 80:
                flash("El apodo no puede superar 80 caracteres.", "error")
            elif len(avatar_url) > 500:
                flash("La URL del avatar es demasiado larga.", "error")
            elif not _is_valid_avatar_url(avatar_url):
                flash("La URL del avatar debe empezar con http:// o https://.", "error")
            else:
                current_user.display_name = display_name or None
                current_user.avatar_url = avatar_url or None
                db.session.commit()
                flash("Perfil actualizado.", "success")
                return redirect(url_for("match.profile"))

        elif form_action == "password":
            current_password = request.form.get("current_password", "")
            new_password = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")

            if not current_user.check_password(current_password):
                flash("La contrasena actual no es correcta.", "error")
            elif len(new_password) < 6:
                flash("La nueva contrasena debe tener al menos 6 caracteres.", "error")
            elif new_password != confirm_password:
                flash("La confirmacion no coincide con la nueva contrasena.", "error")
            else:
                current_user.set_password(new_password)
                db.session.commit()
                flash("Contrasena actualizada.", "success")
                return redirect(url_for("match.profile"))

    predictions = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.updated_at.desc()).all()
    return render_template("profile.html", predictions=predictions)
