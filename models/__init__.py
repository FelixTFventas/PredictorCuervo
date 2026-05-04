from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Inicia sesion para continuar."


from .user import User  # noqa: E402,F401
from .match import Match  # noqa: E402,F401
from .prediction import Prediction  # noqa: E402,F401
