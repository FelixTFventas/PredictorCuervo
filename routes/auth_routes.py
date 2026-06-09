from datetime import datetime, timezone

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from models import db
from models.invitation import Invitation
from models.user import User


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    flash("Solo el administrador puede crear usuarios.", "error")
    return redirect(url_for("auth.login"))


@auth_bp.route("/register/invite/<token>", methods=["GET", "POST"])
def register_invite(token):
    if current_user.is_authenticated:
        return redirect(url_for("match.dashboard"))

    invitation = Invitation.query.filter_by(token=token).first()
    if not invitation or not invitation.is_valid:
        flash("La invitacion no existe, ya fue usada o expiro.", "error")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not email or not password:
            flash("Completa todos los campos.", "error")
        elif len(password) < 6:
            flash("La contrasena debe tener al menos 6 caracteres.", "error")
        elif password != confirm_password:
            flash("La confirmacion no coincide con la contrasena.", "error")
        elif User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Ese usuario o email ya esta registrado.", "error")
        else:
            user = User(username=username, email=email, is_admin=invitation.is_admin)
            user.set_password(password)
            invitation.used_at = datetime.now(timezone.utc).replace(tzinfo=None)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash("Cuenta creada. Bienvenido al predictor.", "success")
            return redirect(url_for("match.dashboard"))

    return render_template("register_invite.html", invitation=invitation)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("match.dashboard"))

    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter((User.username == identifier) | (User.email == identifier.lower())).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Sesion iniciada.", "success")
            return redirect(url_for("match.dashboard"))

        flash("Credenciales invalidas.", "error")

    return render_template("login.html")


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Sesion cerrada.", "success")
    return redirect(url_for("index"))
