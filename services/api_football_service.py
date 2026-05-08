from dataclasses import dataclass
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from flask import current_app


@dataclass
class ApiResult:
    ok: bool
    message: str
    payload: list | None = None


def require_api_key():
    api_key = current_app.config.get("API_FOOTBALL_KEY")
    if not api_key:
        return ApiResult(False, "API-Football no configurada. Define API_FOOTBALL_KEY para sincronizar automaticamente.")
    return ApiResult(True, "API configurada.")


def api_get(path, params=None):
    configured = require_api_key()
    if not configured.ok:
        return configured

    base_url = current_app.config.get("API_FOOTBALL_BASE_URL", "https://v3.football.api-sports.io").rstrip("/")
    query = f"?{urlencode(params)}" if params else ""
    url = f"{base_url}/{path.lstrip('/')}{query}"
    request = Request(url, headers={"x-apisports-key": current_app.config["API_FOOTBALL_KEY"]})

    try:
        with urlopen(request, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        return ApiResult(False, f"API-Football respondio HTTP {exc.code}.")
    except URLError as exc:
        return ApiResult(False, f"No se pudo conectar con API-Football: {exc.reason}")
    except TimeoutError:
        return ApiResult(False, "La consulta a API-Football excedio el tiempo limite.")
    except json.JSONDecodeError:
        return ApiResult(False, "API-Football devolvio una respuesta no valida.")

    errors = data.get("errors")
    if errors:
        return ApiResult(False, f"API-Football devolvio errores: {errors}", data.get("response", []))

    return ApiResult(True, "Consulta API-Football completada.", data.get("response", []))


def check_api_status():
    result = api_get("status")
    if not result.ok:
        return result

    account = result.payload.get("account", {}) if isinstance(result.payload, dict) else {}
    requests = result.payload.get("requests", {}) if isinstance(result.payload, dict) else {}
    message = "API OK"
    if account or requests:
        message = f"API OK. Plan: {account.get('plan', 'N/D')}. Requests hoy: {requests.get('current', 'N/D')}/{requests.get('limit_day', 'N/D')}."
    return ApiResult(True, message, result.payload)


def fetch_colombia_leagues():
    result = api_get("leagues", {"country": "Colombia"})
    if not result.ok:
        return result

    leagues = []
    for item in result.payload or []:
        league = item.get("league", {})
        country = item.get("country", {})
        seasons = [str(season.get("year")) for season in item.get("seasons", []) if season.get("year")]
        leagues.append(
            {
                "id": league.get("id"),
                "name": league.get("name"),
                "type": league.get("type"),
                "country": country.get("name"),
                "seasons": ", ".join(seasons[-6:]),
            }
        )
    return ApiResult(True, f"Ligas encontradas para Colombia: {len(leagues)}.", leagues)


def fetch_liga_betplay_fixtures_preview():
    league_id = current_app.config.get("LIGA_BETPLAY_LEAGUE_ID")
    season = current_app.config.get("LIGA_BETPLAY_SEASON", "2026")
    if not league_id:
        return ApiResult(False, "Define LIGA_BETPLAY_LEAGUE_ID para probar fixtures de Liga BetPlay.")

    result = api_get("fixtures", {"league": league_id, "season": season})
    if not result.ok:
        return result

    fixtures = []
    for item in (result.payload or [])[:30]:
        fixture = item.get("fixture", {})
        teams = item.get("teams", {})
        goals = item.get("goals", {})
        league = item.get("league", {})
        status = fixture.get("status", {})
        fixtures.append(
            {
                "api_id": fixture.get("id"),
                "date": fixture.get("date"),
                "round": league.get("round"),
                "home": teams.get("home", {}).get("name"),
                "away": teams.get("away", {}).get("name"),
                "score": f"{goals.get('home')} - {goals.get('away')}",
                "status": status.get("short"),
            }
        )
    return ApiResult(True, f"Fixtures recibidos: {len(result.payload or [])}. Mostrando hasta 30.", fixtures)


def fetch_worldcup_2026_fixtures():
    configured = require_api_key()
    if not configured.ok:
        return configured
    return ApiResult(False, "Servicio API preparado, pero la integracion real se activa cuando tengas league_id y key validos.")


def fetch_worldcup_2026_results():
    configured = require_api_key()
    if not configured.ok:
        return configured
    return ApiResult(False, "Servicio API preparado, pero la integracion real se activa cuando tengas league_id y key validos.")
