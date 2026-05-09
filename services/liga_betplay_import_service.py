import csv
import os
from dataclasses import dataclass
from datetime import datetime

from models import db
from models.match import Match
from services.competition_service import LIGA_BETPLAY_COMPETITION, LIGA_BETPLAY_SEASON
from services.time_service import local_naive_to_utc_naive


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIGA_BETPLAY_CSV_PATH = os.path.join(BASE_DIR, "data", "liga_betplay_2026_14_partidos.csv")
REQUIRED_COLUMNS = {"Fecha", "Hora", "Fase", "Local", "Visitante", "Estadio"}


@dataclass
class LigaBetPlayImportResult:
    ok: bool
    message: str
    created: int = 0
    updated: int = 0


def _read_rows():
    if not os.path.exists(LIGA_BETPLAY_CSV_PATH):
        raise ValueError(f"No se encontro el CSV: {LIGA_BETPLAY_CSV_PATH}")

    with open(LIGA_BETPLAY_CSV_PATH, encoding="utf-8-sig", newline="") as fixture_file:
        reader = csv.DictReader(fixture_file)
        if not reader.fieldnames or not REQUIRED_COLUMNS.issubset(reader.fieldnames):
            missing = sorted(REQUIRED_COLUMNS - set(reader.fieldnames or []))
            raise ValueError(f"El CSV no tiene las columnas requeridas: {', '.join(missing)}")
        return list(reader)


def _parse_row(row, index):
    for column in REQUIRED_COLUMNS:
        if not row.get(column, "").strip():
            raise ValueError(f"Fila {index + 1}: falta el campo {column}.")

    try:
        starts_at = local_naive_to_utc_naive(datetime.strptime(f"{row['Fecha']} {row['Hora']}", "%Y-%m-%d %H:%M"))
    except ValueError as exc:
        raise ValueError(f"Fila {index + 1}: fecha u hora invalida.") from exc

    stage = row["Fase"].strip()
    return {
        "api_id": f"liga-betplay-2026-{index:03d}",
        "home_team": row["Local"].strip(),
        "away_team": row["Visitante"].strip(),
        "starts_at": starts_at,
        "group_name": LIGA_BETPLAY_COMPETITION,
        "venue": row["Estadio"].strip(),
        "competition": LIGA_BETPLAY_COMPETITION,
        "season": LIGA_BETPLAY_SEASON,
        "round_name": stage,
        "stage": stage,
        "status": "scheduled",
    }


def import_liga_betplay_fixture():
    try:
        rows = _read_rows()
        if len(rows) != 14:
            raise ValueError(f"El CSV debe tener 14 partidos, pero tiene {len(rows)}.")

        created = 0
        updated = 0
        for index, row in enumerate(rows, start=1):
            data = _parse_row(row, index)
            match = Match.query.filter_by(api_id=data["api_id"]).first()
            if match:
                updated += 1
            else:
                match = Match(api_id=data["api_id"])
                db.session.add(match)
                created += 1

            for field, value in data.items():
                setattr(match, field, value)

        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        return LigaBetPlayImportResult(False, str(exc))

    return LigaBetPlayImportResult(
        True,
        f"Liga BetPlay importada: {created} creados, {updated} actualizados.",
        created=created,
        updated=updated,
    )
