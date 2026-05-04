from services.api_football_service import ApiResult, fetch_worldcup_2026_fixtures, fetch_worldcup_2026_results


def sync_fixtures():
    result = fetch_worldcup_2026_fixtures()
    if not result.ok:
        return result
    return ApiResult(True, "Fixture sincronizado.")


def sync_results():
    result = fetch_worldcup_2026_results()
    if not result.ok:
        return result
    return ApiResult(True, "Resultados sincronizados.")
