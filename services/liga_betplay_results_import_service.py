import csv
from dataclasses import dataclass, field
from io import TextIOWrapper

from models import db
from models.match import Match
from services.competition_service import LIGA_BETPLAY_COMPETITION
from services.points_service import update_prediction_points


REQUIRED_COLUMNS = {"api_id", "home_score", "away_score"}
ALLOWED_STATUSES = {"scheduled", "live", "finished", "postponed", "cancelled"}


@dataclass
class ResultsImportSummary:
    ok: bool
    message: str
    updated_matches: int = 0
    recalculated_predictions: int = 0
    errors: list[str] = field(default_factory=list)


def _parse_score(value, row_number, column):
    try:
        score = int((value or "").strip())
    except ValueError as exc:
        raise ValueError(f"Fila {row_number}: {column} debe ser numerico.") from exc

    if score < 0:
        raise ValueError(f"Fila {row_number}: {column} no puede ser negativo.")
    return score


def _validate_headers(fieldnames):
    if not fieldnames:
        return "El CSV no tiene encabezados."
    missing = sorted(REQUIRED_COLUMNS - set(fieldnames))
    if missing:
        return f"El CSV no tiene las columnas requeridas: {', '.join(missing)}."
    return None


def import_liga_betplay_results_csv(file_storage):
    if not file_storage or not file_storage.filename:
        return ResultsImportSummary(False, "Selecciona un archivo CSV.")

    if not file_storage.filename.lower().endswith(".csv"):
        return ResultsImportSummary(False, "El archivo debe ser CSV.")

    summary = ResultsImportSummary(True, "Resultados importados.")

    try:
        stream = TextIOWrapper(file_storage.stream, encoding="utf-8-sig", newline="")
        reader = csv.DictReader(stream)
    except UnicodeDecodeError:
        return ResultsImportSummary(False, "No se pudo leer el CSV. Usa codificacion UTF-8.")

    header_error = _validate_headers(reader.fieldnames)
    if header_error:
        return ResultsImportSummary(False, header_error)

    for row_number, row in enumerate(reader, start=2):
        try:
            api_id = (row.get("api_id") or "").strip()
            if not api_id:
                raise ValueError(f"Fila {row_number}: api_id es obligatorio.")

            match = Match.query.filter_by(api_id=api_id).first()
            if match is None:
                raise ValueError(f"Fila {row_number}: api_id {api_id} no existe.")
            if match.competition != LIGA_BETPLAY_COMPETITION:
                raise ValueError(f"Fila {row_number}: {api_id} no pertenece a Liga BetPlay.")

            status = (row.get("status") or "finished").strip().lower()
            if status not in ALLOWED_STATUSES:
                raise ValueError(f"Fila {row_number}: status {status} no es valido.")

            match.home_score = _parse_score(row.get("home_score"), row_number, "home_score")
            match.away_score = _parse_score(row.get("away_score"), row_number, "away_score")
            match.status = status

            for prediction in match.predictions:
                update_prediction_points(prediction)
                summary.recalculated_predictions += 1

            summary.updated_matches += 1
        except ValueError as exc:
            summary.errors.append(str(exc))

    if summary.updated_matches:
        db.session.commit()
    else:
        db.session.rollback()

    if summary.errors:
        summary.ok = summary.updated_matches > 0
        summary.message = "Resultados importados con advertencias." if summary.ok else "No se importaron resultados."
    else:
        summary.message = "Resultados importados correctamente."

    return summary
