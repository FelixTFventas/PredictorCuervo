from datetime import datetime, timezone

from . import db


class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    home_team = db.Column(db.String(80), nullable=False)
    away_team = db.Column(db.String(80), nullable=False)
    starts_at = db.Column(db.DateTime, nullable=False)
    home_score = db.Column(db.Integer)
    away_score = db.Column(db.Integer)
    group_name = db.Column(db.String(40), nullable=False, default="Fase de grupos")
    venue = db.Column(db.String(120), nullable=False, default="Sede por confirmar")
    api_id = db.Column(db.String(80), unique=True)
    competition = db.Column(db.String(120), nullable=False, default="FIFA World Cup")
    season = db.Column(db.String(20), nullable=False, default="2026")
    round_name = db.Column(db.String(80), nullable=False, default="Fecha por confirmar")
    stage = db.Column(db.String(80), nullable=False, default="Fase de grupos")
    status = db.Column(db.String(20), nullable=False, default="scheduled")
    last_synced_at = db.Column(db.DateTime)

    predictions = db.relationship("Prediction", back_populates="match", cascade="all, delete-orphan")

    @property
    def has_result(self):
        return self.home_score is not None and self.away_score is not None

    @property
    def is_locked(self):
        if self.status in {"live", "finished", "postponed", "cancelled"}:
            return True

        starts_at = self.starts_at
        if starts_at.tzinfo is None:
            starts_at = starts_at.replace(tzinfo=timezone.utc)
        else:
            starts_at = starts_at.astimezone(timezone.utc)
        return datetime.now(timezone.utc) >= starts_at

    @property
    def has_placeholder_teams(self):
        placeholder_terms = ("Clasificado", "Ganador", "Perdedor", "Segundo Grupo", "Mejor tercero")
        teams = (self.home_team or "", self.away_team or "")
        return any(term in team for team in teams for term in placeholder_terms)

    @property
    def can_predict(self):
        return self.status == "scheduled" and not self.has_placeholder_teams and not self.is_locked

    @property
    def status_label(self):
        if self.status == "finished" or self.has_result:
            return "Finalizado"
        if self.status == "live" or self.is_locked:
            return "En juego"
        if self.status == "postponed":
            return "Postergado"
        if self.status == "cancelled":
            return "Cancelado"
        return "Abierto"
