from dataclasses import dataclass

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
