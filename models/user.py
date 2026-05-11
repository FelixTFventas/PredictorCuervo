from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from . import db, login_manager


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    display_name = db.Column(db.String(80))
    avatar_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    predictions = db.relationship("Prediction", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def display_label(self):
        return self.display_name or self.username

    @property
    def avatar_initials(self):
        source = self.display_label or self.email or "?"
        parts = [part for part in source.replace("_", " ").split() if part]
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        return source[:2].upper()

    @property
    def total_points(self):
        return sum(prediction.points or 0 for prediction in self.predictions)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
