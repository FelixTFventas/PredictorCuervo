from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from models import db
from models.champion_pick import ChampionPick
from services.champion_service import available_world_cup_teams, champion_setting, public_champion_rows, recalculate_champion_points, world_cup_started


champion_bp = Blueprint("champion", __name__)


@champion_bp.route("/champion", methods=["GET", "POST"])
@login_required
def champion():
    teams = available_world_cup_teams()
    locked = world_cup_started()
    current_pick = ChampionPick.query.filter_by(user_id=current_user.id).first()

    if request.method == "POST":
        team_name = request.form.get("team_name", "").strip()
        if locked:
            flash("Las elecciones de campeon ya estan cerradas.", "error")
        elif team_name not in teams:
            flash("Selecciona una seleccion valida.", "error")
        else:
            if current_pick is None:
                current_pick = ChampionPick(user_id=current_user.id)
                db.session.add(current_pick)
            current_pick.team_name = team_name
            recalculate_champion_points()
            db.session.commit()
            flash("Campeon guardado.", "success")
            return redirect(url_for("champion.champion"))

    public_rows, summary = public_champion_rows()
    return render_template(
        "champion.html",
        teams=teams,
        locked=locked,
        current_pick=current_pick,
        champion=champion_setting(),
        public_rows=public_rows,
        summary=summary,
    )
