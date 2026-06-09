from collections import Counter
from datetime import datetime, timezone

from models import db
from models.champion_pick import ChampionPick
from models.match import Match
from models.tournament_setting import TournamentSetting
from models.user import User
from services.competition_service import WORLD_CUP_COMPETITION


CHAMPION_SETTING_KEY = "world_cup_champion"
CHAMPION_BONUS_POINTS = 10
PLACEHOLDER_TERMS = ("Clasificado", "Ganador", "Perdedor", "Segundo Grupo", "Mejor tercero")


def available_world_cup_teams():
    teams = set()
    matches = Match.query.filter_by(competition=WORLD_CUP_COMPETITION).all()
    for match in matches:
        for team in (match.home_team, match.away_team):
            if team and not any(term in team for term in PLACEHOLDER_TERMS):
                teams.add(team)
    return sorted(teams)


def world_cup_started():
    first_match = Match.query.filter_by(competition=WORLD_CUP_COMPETITION).order_by(Match.starts_at.asc()).first()
    if not first_match:
        return False
    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    return now_utc >= first_match.starts_at


def champion_setting():
    setting = TournamentSetting.query.filter_by(key=CHAMPION_SETTING_KEY).first()
    return setting.value if setting else None


def set_champion_setting(team_name):
    setting = TournamentSetting.query.filter_by(key=CHAMPION_SETTING_KEY).first()
    if setting is None:
        setting = TournamentSetting(key=CHAMPION_SETTING_KEY, value=team_name)
        db.session.add(setting)
    else:
        setting.value = team_name
    recalculate_champion_points(team_name)


def recalculate_champion_points(champion=None):
    champion = champion if champion is not None else champion_setting()
    for pick in ChampionPick.query.all():
        pick.points = CHAMPION_BONUS_POINTS if champion and pick.team_name == champion else 0


def public_champion_rows():
    picks = {pick.user_id: pick for pick in ChampionPick.query.all()}
    rows = []
    summary = Counter()
    for user in User.query.order_by(User.username.asc()).all():
        pick = picks.get(user.id)
        team_name = pick.team_name if pick else None
        summary[team_name or "Pendiente"] += 1
        rows.append({"user": user, "pick": pick, "team_name": team_name})
    return rows, summary
