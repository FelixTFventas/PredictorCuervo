from datetime import datetime, timezone

from . import db


class Invitation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(120), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    created_by = db.relationship("User")

    @property
    def is_used(self):
        return self.used_at is not None

    @property
    def is_expired(self):
        return datetime.now(timezone.utc).replace(tzinfo=None) >= self.expires_at

    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired
