from dataclasses import dataclass
from datetime import datetime, timedelta

from models import db
from models.match import Match
from services.time_service import local_naive_to_utc_naive


@dataclass
class KnockoutImportResult:
    ok: bool
    message: str
    created: int = 0
    updated: int = 0


KNOCKOUT_MATCHES = [
    *[
        {
            "api_id": f"wc2026-r32-{index:02d}",
            "home_team": f"Clasificado {index * 2 - 1}",
            "away_team": f"Clasificado {index * 2}",
            "starts_at": datetime(2026, 6, 29, [12, 15, 18, 21][(index - 1) % 4]) + timedelta(days=(index - 1) // 4),
            "round_name": f"Dieciseisavos {index}",
            "stage": "Dieciseisavos",
        }
        for index in range(1, 17)
    ],
    *[
        {
            "api_id": f"wc2026-r16-{index:02d}",
            "home_team": f"Ganador Dieciseisavos {index * 2 - 1}",
            "away_team": f"Ganador Dieciseisavos {index * 2}",
            "starts_at": datetime(2026, 7, 4 + ((index - 1) // 4), [12, 15, 18, 21][(index - 1) % 4]),
            "round_name": f"Octavos {index}",
            "stage": "Octavos de final",
        }
        for index in range(1, 9)
    ],
    *[
        {
            "api_id": f"wc2026-qf-{index:02d}",
            "home_team": f"Ganador Octavos {index * 2 - 1}",
            "away_team": f"Ganador Octavos {index * 2}",
            "starts_at": datetime(2026, 7, 9, [12, 15, 18, 21][index - 1]),
            "round_name": f"Cuartos {index}",
            "stage": "Cuartos de final",
        }
        for index in range(1, 5)
    ],
    *[
        {
            "api_id": f"wc2026-sf-{index:02d}",
            "home_team": f"Ganador Cuartos {index * 2 - 1}",
            "away_team": f"Ganador Cuartos {index * 2}",
            "starts_at": datetime(2026, 7, 14 + index - 1, 18),
            "round_name": f"Semifinal {index}",
            "stage": "Semifinales",
        }
        for index in range(1, 3)
    ],
    {
        "api_id": "wc2026-third-place",
        "home_team": "Perdedor Semifinal 1",
        "away_team": "Perdedor Semifinal 2",
        "starts_at": datetime(2026, 7, 18, 18),
        "round_name": "Tercer puesto",
        "stage": "Tercer puesto",
    },
    {
        "api_id": "wc2026-final",
        "home_team": "Ganador Semifinal 1",
        "away_team": "Ganador Semifinal 2",
        "starts_at": datetime(2026, 7, 19, 18),
        "round_name": "Final",
        "stage": "Final",
    },
]


def create_knockout_placeholders():
    created = 0
    updated = 0

    for data in KNOCKOUT_MATCHES:
        match = Match.query.filter_by(api_id=data["api_id"]).first()
        if match:
            updated += 1
        else:
            match = Match(api_id=data["api_id"])
            db.session.add(match)
            created += 1

        match.home_team = data["home_team"]
        match.away_team = data["away_team"]
        match.starts_at = local_naive_to_utc_naive(data["starts_at"])
        match.group_name = "Eliminacion directa"
        match.venue = "Sede por confirmar"
        match.competition = "FIFA World Cup"
        match.season = "2026"
        match.round_name = data["round_name"]
        match.stage = data["stage"]
        match.status = "scheduled"

    db.session.commit()
    return KnockoutImportResult(
        True,
        f"Eliminacion directa creada: {created} creados, {updated} actualizados.",
        created=created,
        updated=updated,
    )
