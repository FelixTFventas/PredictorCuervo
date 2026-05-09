from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from models import db
from models.user import User


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("match.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("Completa todos los campos.", "error")
        elif User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Ese usuario o email ya esta registrado.", "error")
        else:
            admin_email = current_app.config.get("ADMIN_EMAIL")
            is_first_user = User.query.count() == 0
            is_admin = email == admin_email.strip().lower() if admin_email else is_first_user
            user = User(username=username, email=email, is_admin=is_admin)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            message = "Cuenta creada. Ya puedes competir."
            if user.is_admin:
                message = "Cuenta admin creada. Ya puedes gestionar el torneo."
            flash(message, "success")
            return redirect(url_for("match.dashboard"))

    return render_template("register.html")


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
