from . import db


class ChampionPick(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    team_name = db.Column(db.String(80), nullable=False)
    points = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now(), nullable=False)

    user = db.relationship("User")

    __table_args__ = (db.UniqueConstraint("user_id", name="one_champion_pick_per_user"),)
