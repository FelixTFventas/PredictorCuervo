import csv
import os
from dataclasses import dataclass
from datetime import datetime

from models import db
from models.match import Match
from services.time_service import local_naive_to_utc_naive


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
KNOCKOUT_CSV_PATH = os.path.join(BASE_DIR, "data", "fixture_mundial_2026_fases_finales.csv")
REQUIRED_COLUMNS = {"Partido", "Fecha", "Hora", "Fase", "Local", "Visitante", "Sede"}


@dataclass
class KnockoutImportResult:
    ok: bool
    message: str
    created: int = 0
    updated: int = 0


def _read_rows():
    if not os.path.exists(KNOCKOUT_CSV_PATH):
        raise ValueError(f"No se encontro el CSV: {KNOCKOUT_CSV_PATH}")

    with open(KNOCKOUT_CSV_PATH, encoding="utf-8-sig", newline="") as fixture_file:
        reader = csv.DictReader(fixture_file)
        if not reader.fieldnames or not REQUIRED_COLUMNS.issubset(reader.fieldnames):
            missing = sorted(REQUIRED_COLUMNS - set(reader.fieldnames or []))
            raise ValueError(f"El CSV no tiene las columnas requeridas: {', '.join(missing)}")
        return list(reader)


def _api_id(match_number):
    if 73 <= match_number <= 88:
        return f"wc2026-r32-{match_number - 72:02d}"
    if 89 <= match_number <= 96:
        return f"wc2026-r16-{match_number - 88:02d}"
    if 97 <= match_number <= 100:
        return f"wc2026-qf-{match_number - 96:02d}"
    if 101 <= match_number <= 102:
        return f"wc2026-sf-{match_number - 100:02d}"
    if match_number == 103:
        return "wc2026-third-place"
    if match_number == 104:
        return "wc2026-final"
    raise ValueError(f"Partido {match_number} no pertenece a fases finales.")


def _parse_row(row, row_number):
    for column in REQUIRED_COLUMNS:
        if not row.get(column, "").strip():
            raise ValueError(f"Fila {row_number}: falta el campo {column}.")

    try:
        match_number = int(row["Partido"])
    except ValueError as exc:
        raise ValueError(f"Fila {row_number}: Partido debe ser numerico.") from exc

    try:
        starts_at = local_naive_to_utc_naive(datetime.strptime(f"{row['Fecha']} {row['Hora']}", "%Y-%m-%d %H:%M"))
    except ValueError as exc:
        raise ValueError(f"Fila {row_number}: fecha u hora invalida.") from exc

    stage = row["Fase"].strip()
    return {
        "api_id": _api_id(match_number),
        "home_team": row["Local"].strip(),
        "away_team": row["Visitante"].strip(),
        "starts_at": starts_at,
        "group_name": "Eliminacion directa",
        "venue": row["Sede"].strip(),
        "competition": "FIFA World Cup",
        "season": "2026",
        "round_name": f"Partido {match_number}",
        "stage": stage,
        "status": "scheduled",
    }


def create_knockout_placeholders():
    try:
        rows = _read_rows()
        if len(rows) != 32:
            raise ValueError(f"El CSV debe tener 32 partidos, pero tiene {len(rows)}.")

        created = 0
        updated = 0
        for row_number, row in enumerate(rows, start=2):
            data = _parse_row(row, row_number)
            match = Match.query.filter_by(api_id=data["api_id"]).first()
            if match:
                updated += 1
                data.pop("status", None)
            else:
                match = Match(api_id=data["api_id"])
                db.session.add(match)
                created += 1

            for field, value in data.items():
                setattr(match, field, value)

        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        return KnockoutImportResult(False, str(exc))

    return KnockoutImportResult(
        True,
        f"Eliminacion directa creada: {created} creados, {updated} actualizados.",
        created=created,
        updated=updated,
    )
