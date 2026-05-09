from functools import wraps

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from models import db
from models.match import Match
from models.prediction import Prediction
from services.competition_service import LIGA_BETPLAY_COMPETITION, LIGA_BETPLAY_SEASON, WORLD_CUP_COMPETITION, group_matches
from services.api_football_service import check_api_status, fetch_colombia_leagues, fetch_liga_betplay_fixtures_preview
from services.fixture_import_service import import_group_fixture
from services.forebet_result_service import sync_liga_betplay_results_from_forebet
from services.knockout_fixture_service import create_knockout_placeholders
from services.liga_betplay_import_service import import_liga_betplay_fixture
from services.liga_betplay_results_import_service import import_liga_betplay_results_csv
from services.points_service import update_prediction_points
from services.sync_service import sync_fixtures, sync_results
from services.time_service import parse_local_datetime


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


def apply_match_form(match):
    match.home_team = request.form.get("home_team", "").strip()
    match.away_team = request.form.get("away_team", "").strip()
    match.starts_at = parse_local_datetime(request.form.get("starts_at", ""))
    match.group_name = request.form.get("group_name", "").strip() or "Fase de grupos"
    match.venue = request.form.get("venue", "").strip() or "Sede por confirmar"
    match.competition = request.form.get("competition", "").strip() or "FIFA World Cup"
    match.season = request.form.get("season", "").strip() or "2026"
    match.round_name = request.form.get("round_name", "").strip() or "Fecha por confirmar"
    match.stage = request.form.get("stage", "").strip() or match.group_name
    match.status = request.form.get("status", "scheduled")
    match.api_id = request.form.get("api_id", "").strip() or None


def validate_match_form(match):
    if not match.home_team or not match.away_team:
        return "Completa los equipos."
    if match.status not in MATCH_STATUSES:
        return "El estado del partido no es valido."
    if match.api_id:
        duplicate = Match.query.filter(Match.api_id == match.api_id, Match.id != match.id).first()
        if duplicate:
            return "El API ID ya esta usado por otro partido."
    return None


def recalculate_match_points(match):
    for prediction in match.predictions:
        update_prediction_points(prediction)


@admin_bp.route("/")
@admin_required
def dashboard():
    world_cup_matches = Match.query.filter_by(competition=WORLD_CUP_COMPETITION).count()
    liga_betplay_matches_count = Match.query.filter_by(competition=LIGA_BETPLAY_COMPETITION, season=LIGA_BETPLAY_SEASON).count()
    finished_matches = Match.query.filter_by(competition=WORLD_CUP_COMPETITION, status="finished").count()
    predictions_count = Prediction.query.count()
    return render_template(
        "admin/dashboard.html",
        world_cup_matches=world_cup_matches,
        liga_betplay_matches_count=liga_betplay_matches_count,
        finished_matches=finished_matches,
        predictions_count=predictions_count,
        api_configured=bool(current_app.config.get("API_FOOTBALL_KEY")),
    )


@admin_bp.route("/matches")
@admin_required
def matches():
    matches_list = Match.query.filter_by(competition=WORLD_CUP_COMPETITION).order_by(Match.starts_at.asc()).all()
    return render_template(
        "admin/matches.html",
        grouped_matches=group_matches(matches_list),
        page_title="Partidos Mundial",
        page_description="Gestiona fixture, resultados y cruces del Mundial.",
        return_to="admin.matches",
        team_display="flags",
    )


@admin_bp.route("/liga-betplay/matches")
@admin_required
def liga_betplay_matches():
    matches_list = (
        Match.query.filter_by(competition=LIGA_BETPLAY_COMPETITION, season=LIGA_BETPLAY_SEASON)
        .order_by(Match.starts_at.asc())
        .all()
    )
    return render_template(
        "admin/matches.html",
        grouped_matches=group_matches(matches_list),
        page_title="Partidos Liga BetPlay",
        page_description="Gestiona la fase final de Liga BetPlay sin mezclarla con el Mundial.",
        return_to="admin.liga_betplay_matches",
        team_display="clubs",
    )


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

        form_error = validate_match_form(match)
        if form_error:
            flash(form_error, "error")
        else:
            db.session.add(match)
            db.session.commit()
            flash("Partido creado.", "success")
            return redirect(url_for("admin.liga_betplay_matches" if match.competition == LIGA_BETPLAY_COMPETITION else "admin.matches"))

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

        form_error = validate_match_form(match)
        if form_error:
            flash(form_error, "error")
            return render_template("admin/match_form.html", match=match, statuses=MATCH_STATUSES)

        if match.status == "finished" and match.has_result:
            recalculate_match_points(match)
        db.session.commit()
        flash("Partido actualizado.", "success")
        return redirect(url_for("admin.liga_betplay_matches" if match.competition == LIGA_BETPLAY_COMPETITION else "admin.matches"))

    return render_template("admin/match_form.html", match=match, statuses=MATCH_STATUSES)


@admin_bp.route("/matches/<int:match_id>/result", methods=["POST"])
@admin_required
def save_result(match_id):
    match = Match.query.get_or_404(match_id)
    return_to = request.form.get("return_to")
    redirect_endpoint = "admin.liga_betplay_matches" if return_to == "admin.liga_betplay_matches" or match.competition == LIGA_BETPLAY_COMPETITION else "admin.matches"
    try:
        match.home_score = int(request.form.get("home_score", ""))
        match.away_score = int(request.form.get("away_score", ""))
    except ValueError:
        flash("Ingresa un resultado valido.", "error")
        return redirect(url_for(redirect_endpoint))

    if match.home_score < 0 or match.away_score < 0:
        flash("Los goles no pueden ser negativos.", "error")
        return redirect(url_for(redirect_endpoint))

    match.status = "finished"
    recalculate_match_points(match)
    db.session.commit()
    flash("Resultado guardado y puntos recalculados.", "success")
    return redirect(url_for(redirect_endpoint))


@admin_bp.route("/recalculate-points", methods=["POST"])
@admin_required
def recalculate_points():
    for prediction in Prediction.query.all():
        update_prediction_points(prediction)
    db.session.commit()
    flash("Puntos recalculados.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/import-group-fixture", methods=["POST"])
@admin_required
def import_group_fixture_route():
    result = import_group_fixture()
    flash(result.message, "success" if result.ok else "error")
    return redirect(url_for("admin.matches" if result.ok else "admin.dashboard"))


@admin_bp.route("/import-liga-betplay", methods=["POST"])
@admin_required
def import_liga_betplay_route():
    result = import_liga_betplay_fixture()
    flash(result.message, "success" if result.ok else "error")
    return redirect(url_for("admin.liga_betplay_matches" if result.ok else "admin.dashboard"))


@admin_bp.route("/liga-betplay/import-results", methods=["GET", "POST"])
@admin_required
def import_liga_betplay_results_route():
    summary = None
    if request.method == "POST":
        summary = import_liga_betplay_results_csv(request.files.get("results_csv"))
        flash(summary.message, "success" if summary.ok else "error")
    return render_template("admin/import_liga_betplay_results.html", summary=summary)


@admin_bp.route("/liga-betplay/sync-forebet-results", methods=["POST"])
@admin_required
def sync_liga_betplay_forebet_results_route():
    summary = sync_liga_betplay_results_from_forebet()
    flash(summary.message, "success" if summary.ok else "error")
    for skipped in summary.skipped[:3]:
        flash(skipped, "error")
    if len(summary.skipped) > 3:
        flash(f"{len(summary.skipped) - 3} partidos adicionales no fueron confirmados.", "error")
    return redirect(url_for("admin.liga_betplay_matches" if summary.updated_matches else "admin.dashboard"))


@admin_bp.route("/api-football/status", methods=["POST"])
@admin_required
def api_football_status_route():
    result = check_api_status()
    return render_template("admin/api_diagnostics.html", title="Estado API-Football", result=result, rows=[])


@admin_bp.route("/api-football/colombia-leagues", methods=["POST"])
@admin_required
def api_football_colombia_leagues_route():
    result = fetch_colombia_leagues()
    columns = ["id", "name", "type", "country", "seasons"]
    return render_template("admin/api_diagnostics.html", title="Ligas Colombia API-Football", result=result, rows=result.payload or [], columns=columns)


@admin_bp.route("/api-football/liga-betplay-fixtures", methods=["POST"])
@admin_required
def api_football_liga_betplay_fixtures_route():
    result = fetch_liga_betplay_fixtures_preview()
    columns = ["api_id", "date", "round", "home", "away", "score", "status"]
    return render_template("admin/api_diagnostics.html", title="Fixtures Liga BetPlay API-Football", result=result, rows=result.payload or [], columns=columns)


@admin_bp.route("/create-knockout-placeholders", methods=["POST"])
@admin_required
def create_knockout_placeholders_route():
    result = create_knockout_placeholders()
    flash(result.message, "success" if result.ok else "error")
    return redirect(url_for("admin.matches"))


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
