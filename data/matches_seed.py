from datetime import datetime, timedelta, timezone

from models import db
from models.match import Match
from models.prediction import Prediction
from services.points_service import update_prediction_points


SEED_MATCHES = [
    ("Argentina", "Brasil", 1, "Grupo A", "Estadio Monumental Cuervo"),
    ("Francia", "Alemania", 2, "Grupo B", "Arena del Puerto"),
    ("Espana", "Italia", 3, "Grupo C", "Estadio Central"),
    ("Uruguay", "Portugal", 4, "Grupo D", "La Fortaleza"),
    ("Inglaterra", "Paises Bajos", 5, "Grupo E", "Estadio Norte"),
    ("Mexico", "Colombia", 6, "Grupo F", "Parque Mundialista"),
]


def seed_matches():
    if Match.query.first():
        return

    base_date = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0) + timedelta(days=1)

    for home_team, away_team, day_offset, group_name, venue in SEED_MATCHES:
        match = Match(
            home_team=home_team,
            away_team=away_team,
            starts_at=base_date + timedelta(days=day_offset),
            group_name=group_name,
            venue=venue,
        )
        db.session.add(match)

    db.session.commit()


def recalculate_all_points():
    for prediction in Prediction.query.all():
        update_prediction_points(prediction)
    db.session.commit()
