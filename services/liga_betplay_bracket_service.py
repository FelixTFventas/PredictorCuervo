from dataclasses import dataclass

from models import db
from models.match import Match


@dataclass(frozen=True)
class TwoLegTie:
    first_leg_api_id: str
    second_leg_api_id: str


QUARTERFINAL_TIES = {
    1: TwoLegTie("liga-betplay-2026-001", "liga-betplay-2026-005"),
    2: TwoLegTie("liga-betplay-2026-002", "liga-betplay-2026-007"),
    3: TwoLegTie("liga-betplay-2026-003", "liga-betplay-2026-006"),
    4: TwoLegTie("liga-betplay-2026-004", "liga-betplay-2026-008"),
}
SEMIFINAL_TIES = {
    1: TwoLegTie("liga-betplay-2026-009", "liga-betplay-2026-011"),
    2: TwoLegTie("liga-betplay-2026-010", "liga-betplay-2026-012"),
}


def update_liga_betplay_bracket(commit=True):
    updated = 0

    quarter_winners = {tie_number: _tie_winner(tie) for tie_number, tie in QUARTERFINAL_TIES.items()}
    updated += _set_two_leg_teams(SEMIFINAL_TIES[1], quarter_winners.get(1), quarter_winners.get(2))
    updated += _set_two_leg_teams(SEMIFINAL_TIES[2], quarter_winners.get(3), quarter_winners.get(4))

    semifinal_winners = {tie_number: _tie_winner(tie) for tie_number, tie in SEMIFINAL_TIES.items()}
    updated += _set_two_leg_teams(
        TwoLegTie("liga-betplay-2026-013", "liga-betplay-2026-014"),
        semifinal_winners.get(1),
        semifinal_winners.get(2),
    )

    if updated and commit:
        db.session.commit()
    return updated


def _match(api_id):
    return Match.query.filter_by(api_id=api_id).first()


def _tie_winner(tie):
    first_leg = _match(tie.first_leg_api_id)
    second_leg = _match(tie.second_leg_api_id)
    if not first_leg or not second_leg or not first_leg.has_result or not second_leg.has_result:
        return None

    first_team = first_leg.home_team
    second_team = first_leg.away_team
    first_team_goals = first_leg.home_score + second_leg.away_score
    second_team_goals = first_leg.away_score + second_leg.home_score

    if first_team_goals == second_team_goals:
        return None
    return first_team if first_team_goals > second_team_goals else second_team


def _set_two_leg_teams(tie, first_winner, second_winner):
    first_leg = _match(tie.first_leg_api_id)
    second_leg = _match(tie.second_leg_api_id)
    if not first_leg or not second_leg:
        return 0

    updated = 0
    updated += _set_match_teams(first_leg, first_winner or first_leg.home_team, second_winner or first_leg.away_team)
    updated += _set_match_teams(second_leg, second_winner or second_leg.home_team, first_winner or second_leg.away_team)
    return updated


def _set_match_teams(match, home_team, away_team):
    if not match.has_placeholder_teams:
        return 0

    if match.home_team == home_team and match.away_team == away_team:
        return 0
    match.home_team = home_team
    match.away_team = away_team
    return 1
