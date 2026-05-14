import html
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from models import db
from models.match import Match
from services.competition_service import LIGA_BETPLAY_COMPETITION, LIGA_BETPLAY_SEASON
from services.liga_betplay_bracket_service import update_liga_betplay_bracket
from services.points_service import update_prediction_points
from services.time_service import app_timezone, utc_naive_to_local


FOREBET_URLS = [
    "https://www.forebet.com/",
    "https://www.forebet.com/en/football-predictions-from-yesterday",
]

TEAM_ALIASES = {
    "america": "america de cali",
    "america cali": "america de cali",
    "atl nacional": "atletico nacional",
    "atletico nacional": "atletico nacional",
    "dep pasto": "deportivo pasto",
    "deportes tolima": "deportes tolima",
    "tolima": "deportes tolima",
    "ind santa fe": "independiente santa fe",
    "independiente santa fe": "independiente santa fe",
    "junior": "junior fc",
    "junior fc": "junior fc",
    "la equidad": "internacional de bogota",
    "inter bogota": "internacional de bogota",
    "internacional bogota": "internacional de bogota",
    "internacional de bogota": "internacional de bogota",
    "once caldas": "once caldas",
}


@dataclass
class ForebetMatchResult:
    home_team: str
    away_team: str
    match_date: datetime.date
    home_score: int
    away_score: int
    source_url: str


@dataclass
class ForebetSyncSummary:
    ok: bool
    message: str
    pending_matches: int = 0
    forebet_results: int = 0
    updated_matches: int = 0
    recalculated_predictions: int = 0
    skipped: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def sync_liga_betplay_results_from_forebet():
    target_dates = _target_dates()
    pending_matches = _pending_liga_matches(target_dates)
    summary = ForebetSyncSummary(True, "Consulta Forebet completada.", pending_matches=len(pending_matches))

    if not pending_matches:
        summary.message = "Forebet: no hay partidos pendientes de Liga BetPlay para hoy o ayer."
        return summary

    try:
        forebet_results = fetch_forebet_results(target_dates)
    except ValueError as exc:
        summary.ok = False
        summary.message = str(exc)
        summary.errors.append(str(exc))
        return summary

    summary.forebet_results = len(forebet_results)
    for match in pending_matches:
        candidates = [result for result in forebet_results if _same_match(match, result)]
        if len(candidates) != 1:
            reason = "sin coincidencia" if not candidates else "coincidencia ambigua"
            summary.skipped.append(f"{match.home_team} vs {match.away_team}: {reason} en Forebet.")
            continue

        result = candidates[0]
        match.home_score = result.home_score
        match.away_score = result.away_score
        match.status = "finished"
        for prediction in match.predictions:
            update_prediction_points(prediction)
            summary.recalculated_predictions += 1
        summary.updated_matches += 1

    if summary.updated_matches:
        update_liga_betplay_bracket(commit=False)
        db.session.commit()
    else:
        db.session.rollback()

    if summary.updated_matches:
        summary.message = (
            f"Forebet: {summary.updated_matches} resultados actualizados, "
            f"{len(summary.skipped)} no confirmados."
        )
    else:
        summary.ok = False
        summary.message = "Forebet: no se confirmo ningun resultado pendiente."

    return summary


def fetch_forebet_results(target_dates):
    results = []
    errors = []
    for url in FOREBET_URLS:
        try:
            page = _fetch_forebet_page(url)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        results.extend(_parse_forebet_page(page, url, target_dates))

    if not results and errors:
        raise ValueError("No se pudo consultar Forebet: " + " ".join(errors))
    return results


def _target_dates():
    today = datetime.now(app_timezone()).date()
    return {today, today - timedelta(days=1)}


def _pending_liga_matches(target_dates):
    matches = (
        Match.query.filter_by(competition=LIGA_BETPLAY_COMPETITION, season=LIGA_BETPLAY_SEASON)
        .filter(Match.status != "finished")
        .order_by(Match.starts_at.asc())
        .all()
    )
    return [match for match in matches if utc_naive_to_local(match.starts_at).date() in target_dates]


def _fetch_forebet_page(url):
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
        },
    )
    try:
        with urlopen(request, timeout=20) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset, "replace")
    except HTTPError as exc:
        raise ValueError(f"Forebet respondio HTTP {exc.code}.") from exc
    except URLError as exc:
        raise ValueError(f"No se pudo conectar con Forebet: {exc.reason}") from exc
    except TimeoutError as exc:
        raise ValueError("La consulta a Forebet excedio el tiempo limite.") from exc


def _parse_forebet_page(page, source_url, target_dates):
    results = []
    for row in re.split(r"<div class=['\"]rcnt", page):
        if "Primera A" not in row or "Colombia" not in row:
            continue
        if ">FT<" not in row:
            continue

        home_team = _extract_team(row, "homeTeam")
        away_team = _extract_team(row, "awayTeam")
        date_match = re.search(r"<span class=['\"]date_bah['\"]>(.*?)</span>", row, re.DOTALL)
        score_match = re.search(r"<b class=['\"]l_scr['\"]>\s*(\d+)\s*-\s*(\d+)\s*</b>", row, re.DOTALL)
        if not home_team or not away_team or not date_match or not score_match:
            continue

        try:
            match_date = datetime.strptime(_clean_text(date_match.group(1)), "%d/%m/%Y %H:%M").date()
        except ValueError:
            continue
        if match_date not in target_dates:
            continue

        results.append(
            ForebetMatchResult(
                home_team=home_team,
                away_team=away_team,
                match_date=match_date,
                home_score=int(score_match.group(1)),
                away_score=int(score_match.group(2)),
                source_url=source_url,
            )
        )
    return results


def _extract_team(row, class_name):
    match = re.search(
        rf"<span class=['\"]{class_name}['\"][^>]*>.*?<span itemprop=['\"]name['\"]>(.*?)</span>",
        row,
        re.DOTALL,
    )
    return _clean_text(match.group(1)) if match else None


def _same_match(match, result):
    return (
        utc_naive_to_local(match.starts_at).date() == result.match_date
        and _canonical_team(match.home_team) == _canonical_team(result.home_team)
        and _canonical_team(match.away_team) == _canonical_team(result.away_team)
    )


def _canonical_team(name):
    normalized = _normalize_text(name)
    return TEAM_ALIASES.get(normalized, normalized)


def _normalize_text(value):
    value = _clean_text(value).replace("�", "e")
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^a-zA-Z0-9]+", " ", value).strip().lower()
    return re.sub(r"\s+", " ", value)


def _clean_text(value):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", value or ""))).strip()
