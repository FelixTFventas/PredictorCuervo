from flask import Blueprint, jsonify, request

from models.match import Match
from services.competition_service import LIGA_BETPLAY_COMPETITION, LIGA_BETPLAY_SEASON
from services.liga_betplay_results_import_service import import_liga_betplay_results_csv_text


api_results_bp = Blueprint("api_results", __name__, url_prefix="/api")


def _match_result_json(match):
    return {
        "api_id": match.api_id,
        "equipo_local": match.home_team,
        "equipo_visitante": match.away_team,
        "goles_local": match.home_score,
        "goles_visitante": match.away_score,
        "estado": match.status,
    }


@api_results_bp.route("/resultados/csv", methods=["POST"])
def cargar_resultados_csv():
    summary = import_liga_betplay_results_csv_text(request.get_data(as_text=True))
    status_code = 200 if summary.ok else 400
    return jsonify(
        {
            "mensaje": summary.message,
            "actualizados": summary.updated_matches,
            "predicciones_recalculadas": summary.recalculated_predictions,
            "errores": summary.errors,
            "resultados": [_match_result_json(match) for match in _finished_liga_betplay_matches()],
        }
    ), status_code


@api_results_bp.route("/resultados", methods=["GET"])
def listar_resultados():
    return jsonify([_match_result_json(match) for match in _finished_liga_betplay_matches()])


def _finished_liga_betplay_matches():
    return (
        Match.query.filter(
            Match.competition == LIGA_BETPLAY_COMPETITION,
            Match.season == LIGA_BETPLAY_SEASON,
            Match.home_score.isnot(None),
            Match.away_score.isnot(None),
        )
        .order_by(Match.starts_at.asc())
        .all()
    )
