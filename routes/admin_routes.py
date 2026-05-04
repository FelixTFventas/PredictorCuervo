from datetime import datetime
from functools import wraps

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from models import db
from models.match import Match
from models.prediction import Prediction
from services.points_service import update_prediction_points
from services.sync_service import sync_fixtures, sync_results


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

MATCH_STATUSES = ["scheduled", "live", "finished", "postponed", "cancelled"]


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_admin:
            flash("No tienes permisos para acceder al panel admin.", "error")
            return redirect(url_for("match.dashboard"))
        return view(*args, **kwargs)

    return wrapped


def parse_datetime(value):
    return datetime.strptime(value, "%Y-%m-%dT%H:%M")


def apply_match_form(match):
    match.home_team = request.form.get("home_team", "").strip()
    match.away_team = request.form.get("away_team", "").strip()
    match.starts_at = parse_datetime(request.form.get("starts_at", ""))
    match.group_name = request.form.get("group_name", "").strip() or "Fase de grupos"
    match.venue = request.form.get("venue", "").strip() or "Sede por confirmar"
    match.competition = request.form.get("competition", "").strip() or "FIFA World Cup"
    match.season = request.form.get("season", "").strip() or "2026"
    match.round_name = request.form.get("round_name", "").strip() or "Fecha por confirmar"
    match.stage = request.form.get("stage", "").strip() or match.group_name
    match.status = request.form.get("status", "scheduled")
    match.api_id = request.form.get("api_id", "").strip() or None


def recalculate_match_points(match):
    for prediction in match.predictions:
        update_prediction_points(prediction)


@admin_bp.route("/")
@admin_required
def dashboard():
    total_matches = Match.query.count()
    finished_matches = Match.query.filter_by(status="finished").count()
    predictions_count = Prediction.query.count()
    return render_template(
        "admin/dashboard.html",
        total_matches=total_matches,
        finished_matches=finished_matches,
        predictions_count=predictions_count,
        api_configured=bool(current_app.config.get("API_FOOTBALL_KEY")),
    )


@admin_bp.route("/matches")
@admin_required
def matches():
    matches_list = Match.query.order_by(Match.starts_at.asc()).all()
    return render_template("admin/matches.html", matches=matches_list)


@admin_bp.route("/matches/new", methods=["GET", "POST"])
@admin_required
def new_match():
    match = Match()
    if request.method == "POST":
        try:
            apply_match_form(match)
        except ValueError:
            flash("La fecha del partido no es valida.", "error")
            return render_template("admin/match_form.html", match=match, statuses=MATCH_STATUSES)

        if not match.home_team or not match.away_team:
            flash("Completa los equipos.", "error")
        else:
            db.session.add(match)
            db.session.commit()
            flash("Partido creado.", "success")
            return redirect(url_for("admin.matches"))

    return render_template("admin/match_form.html", match=match, statuses=MATCH_STATUSES)


@admin_bp.route("/matches/<int:match_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_match(match_id):
    match = Match.query.get_or_404(match_id)
    if request.method == "POST":
        try:
            apply_match_form(match)
        except ValueError:
            flash("La fecha del partido no es valida.", "error")
            return render_template("admin/match_form.html", match=match, statuses=MATCH_STATUSES)

        if match.status == "finished" and match.has_result:
            recalculate_match_points(match)
        db.session.commit()
        flash("Partido actualizado.", "success")
        return redirect(url_for("admin.matches"))

    return render_template("admin/match_form.html", match=match, statuses=MATCH_STATUSES)


@admin_bp.route("/matches/<int:match_id>/result", methods=["POST"])
@admin_required
def save_result(match_id):
    match = Match.query.get_or_404(match_id)
    try:
        match.home_score = int(request.form.get("home_score", ""))
        match.away_score = int(request.form.get("away_score", ""))
    except ValueError:
        flash("Ingresa un resultado valido.", "error")
        return redirect(url_for("admin.matches"))

    if match.home_score < 0 or match.away_score < 0:
        flash("Los goles no pueden ser negativos.", "error")
        return redirect(url_for("admin.matches"))

    match.status = "finished"
    recalculate_match_points(match)
    db.session.commit()
    flash("Resultado guardado y puntos recalculados.", "success")
    return redirect(url_for("admin.matches"))


@admin_bp.route("/recalculate-points", methods=["POST"])
@admin_required
def recalculate_points():
    for prediction in Prediction.query.all():
        update_prediction_points(prediction)
    db.session.commit()
    flash("Puntos recalculados.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/sync-fixtures", methods=["POST"])
@admin_required
def sync_fixtures_route():
    result = sync_fixtures()
    flash(result.message, "success" if result.ok else "error")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/sync-results", methods=["POST"])
@admin_required
def sync_results_route():
    result = sync_results()
    flash(result.message, "success" if result.ok else "error")
    return redirect(url_for("admin.dashboard"))
