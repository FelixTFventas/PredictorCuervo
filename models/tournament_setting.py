from . import db


class TournamentSetting(db.Model):
    key = db.Column(db.String(80), primary_key=True)
    value = db.Column(db.String(160), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now(), nullable=False)
