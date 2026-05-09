import csv
import os
from dataclasses import dataclass
from datetime import datetime

from models import db
from models.match import Match
from services.time_service import local_naive_to_utc_naive


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FIXTURE_CSV_PATH = os.path.join(BASE_DIR, "data", "fixture_mundial_2026_72_partidos_validado.csv")
REQUIRED_COLUMNS = {"Partido", "Fecha", "Hora", "Grupo", "Local", "Visitante", "Sede", "Fase"}


@dataclass
class ImportResult:
    ok: bool
    message: str
    created: int = 0
    updated: int = 0
    deleted_demo: int = 0


def _read_fixture_rows():
    if not os.path.exists(FIXTURE_CSV_PATH):
        raise ValueError(f"No se encontro el CSV: {FIXTURE_CSV_PATH}")

    with open(FIXTURE_CSV_PATH, encoding="utf-8-sig", newline="") as fixture_file:
        reader = csv.DictReader(fixture_file)
        if not reader.fieldnames or not REQUIRED_COLUMNS.issubset(reader.fieldnames):
            missing = sorted(REQUIRED_COLUMNS - set(reader.fieldnames or []))
            raise ValueError(f"El CSV no tiene las columnas requeridas: {', '.join(missing)}")
        return list(reader)


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

    return {
        "api_id": f"wc2026-group-{match_number:03d}",
        "home_team": row["Local"].strip(),
        "away_team": row["Visitante"].strip(),
        "starts_at": starts_at,
        "group_name": row["Grupo"].strip(),
        "venue": row["Sede"].strip(),
        "competition": "FIFA World Cup",
        "season": "2026",
        "round_name": row["Grupo"].strip(),
        "stage": row["Fase"].strip(),
        "status": "scheduled",
    }


def _delete_demo_matches_if_safe():
    matches = Match.query.order_by(Match.id.asc()).all()
    if len(matches) != 6:
        return 0
    if any(match.predictions for match in matches):
        return 0
    if any(match.api_id for match in matches):
        return 0

    for match in matches:
        db.session.delete(match)
    db.session.flush()
    return len(matches)


def import_group_fixture():
    try:
        rows = _read_fixture_rows()
        if len(rows) != 72:
            raise ValueError(f"El CSV debe tener 72 partidos, pero tiene {len(rows)}.")

        deleted_demo = _delete_demo_matches_if_safe()
        created = 0
        updated = 0

        for row_number, row in enumerate(rows, start=2):
            data = _parse_row(row, row_number)
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
        return ImportResult(False, str(exc))

    return ImportResult(
        True,
        f"Fixture importado: {created} creados, {updated} actualizados, {deleted_demo} demo eliminados.",
        created=created,
        updated=updated,
        deleted_demo=deleted_demo,
    )
