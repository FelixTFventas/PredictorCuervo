from . import db


class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey("match.id"), nullable=False)
    pred_home_score = db.Column(db.Integer, nullable=False)
    pred_away_score = db.Column(db.Integer, nullable=False)
    points = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now(), nullable=False)

    user = db.relationship("User", back_populates="predictions")
    match = db.relationship("Match", back_populates="predictions")

    __table_args__ = (db.UniqueConstraint("user_id", "match_id", name="one_prediction_per_match"),)
