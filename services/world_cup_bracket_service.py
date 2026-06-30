from dataclasses import dataclass, field

from models import db
from models.match import Match
from services.competition_service import WORLD_CUP_COMPETITION


GROUPS = tuple("ABCDEFGHIJKL")
GROUP_MATCHES_REQUIRED = 6
THIRD_PLACE_SLOTS = ("A", "B", "D", "E", "G", "I", "K", "L")

FIXED_ROUND_OF_32_MATCHES = {
    "wc2026-r32-01": ("2A", "2B"),
    "wc2026-r32-03": ("1F", "2C"),
    "wc2026-r32-04": ("1C", "2F"),
    "wc2026-r32-06": ("2E", "2I"),
    "wc2026-r32-11": ("2K", "2L"),
    "wc2026-r32-12": ("1H", "2J"),
    "wc2026-r32-14": ("1J", "2H"),
    "wc2026-r32-16": ("2D", "2G"),
}

THIRD_PLACE_ROUND_OF_32_MATCHES = {
    "A": "wc2026-r32-07",
    "B": "wc2026-r32-13",
    "D": "wc2026-r32-09",
    "E": "wc2026-r32-02",
    "G": "wc2026-r32-10",
    "I": "wc2026-r32-05",
    "K": "wc2026-r32-15",
    "L": "wc2026-r32-08",
}

KNOCKOUT_ADVANCEMENT_MATCHES = {
    "wc2026-r16-01": (("winner", "wc2026-r32-02"), ("winner", "wc2026-r32-05")),
    "wc2026-r16-02": (("winner", "wc2026-r32-01"), ("winner", "wc2026-r32-03")),
    "wc2026-r16-03": (("winner", "wc2026-r32-04"), ("winner", "wc2026-r32-06")),
    "wc2026-r16-04": (("winner", "wc2026-r32-07"), ("winner", "wc2026-r32-08")),
    "wc2026-r16-05": (("winner", "wc2026-r32-11"), ("winner", "wc2026-r32-12")),
    "wc2026-r16-06": (("winner", "wc2026-r32-09"), ("winner", "wc2026-r32-10")),
    "wc2026-r16-07": (("winner", "wc2026-r32-14"), ("winner", "wc2026-r32-16")),
    "wc2026-r16-08": (("winner", "wc2026-r32-13"), ("winner", "wc2026-r32-15")),
    "wc2026-qf-01": (("winner", "wc2026-r16-01"), ("winner", "wc2026-r16-02")),
    "wc2026-qf-02": (("winner", "wc2026-r16-05"), ("winner", "wc2026-r16-06")),
    "wc2026-qf-03": (("winner", "wc2026-r16-03"), ("winner", "wc2026-r16-04")),
    "wc2026-qf-04": (("winner", "wc2026-r16-07"), ("winner", "wc2026-r16-08")),
    "wc2026-sf-01": (("winner", "wc2026-qf-01"), ("winner", "wc2026-qf-02")),
    "wc2026-sf-02": (("winner", "wc2026-qf-03"), ("winner", "wc2026-qf-04")),
    "wc2026-third-place": (("loser", "wc2026-sf-01"), ("loser", "wc2026-sf-02")),
    "wc2026-final": (("winner", "wc2026-sf-01"), ("winner", "wc2026-sf-02")),
}

KNOCKOUT_TARGET_PLACEHOLDERS = {
    "wc2026-r16-01": ("Ganador Partido 74", "Ganador Partido 77"),
    "wc2026-r16-02": ("Ganador Partido 73", "Ganador Partido 75"),
    "wc2026-r16-03": ("Ganador Partido 76", "Ganador Partido 78"),
    "wc2026-r16-04": ("Ganador Partido 79", "Ganador Partido 80"),
    "wc2026-r16-05": ("Ganador Partido 83", "Ganador Partido 84"),
    "wc2026-r16-06": ("Ganador Partido 81", "Ganador Partido 82"),
    "wc2026-r16-07": ("Ganador Partido 86", "Ganador Partido 88"),
    "wc2026-r16-08": ("Ganador Partido 85", "Ganador Partido 87"),
    "wc2026-qf-01": ("Ganador Partido 89", "Ganador Partido 90"),
    "wc2026-qf-02": ("Ganador Partido 93", "Ganador Partido 94"),
    "wc2026-qf-03": ("Ganador Partido 91", "Ganador Partido 92"),
    "wc2026-qf-04": ("Ganador Partido 95", "Ganador Partido 96"),
    "wc2026-sf-01": ("Ganador Partido 97", "Ganador Partido 98"),
    "wc2026-sf-02": ("Ganador Partido 99", "Ganador Partido 100"),
    "wc2026-third-place": ("Perdedor Partido 101", "Perdedor Partido 102"),
    "wc2026-final": ("Ganador Partido 101", "Ganador Partido 102"),
}

# FIFA World Cup 26 Regulations, Annexe C. Each string is ordered as:
# 1A, 1B, 1D, 1E, 1G, 1I, 1K, 1L.
ANNEX_C_OPTIONS = (
    'EJIFHGLK',
    'HGIDJFLK',
    'EJIDHGLK',
    'EJIDHFLK',
    'EGIDJFLK',
    'EGJDHFLK',
    'EGIDHFLK',
    'EGJDHFLI',
    'EGJDHFIK',
    'HGICJFLK',
    'EJICHGLK',
    'EJICHFLK',
    'EGICJFLK',
    'EGJCHFLK',
    'EGICHFLK',
    'EGJCHFLI',
    'EGJCHFIK',
    'HGICJDLK',
    'CJIDHFLK',
    'CGIDJFLK',
    'CGJDHFLK',
    'CGIDHFLK',
    'CGJDHFLI',
    'CGJDHFIK',
    'EJICHDLK',
    'EGICJDLK',
    'EGJCHDLK',
    'EGICHDLK',
    'EGJCHDLI',
    'EGJCHDIK',
    'CJEDIFLK',
    'CJEDHFLK',
    'CEIDHFLK',
    'CJEDHFLI',
    'CJEDHFIK',
    'CGEDJFLK',
    'CGEDIFLK',
    'CGEDJFLI',
    'CGEDJFIK',
    'CGEDHFLK',
    'CGJDHFLE',
    'CGJDHFEK',
    'CGEDHFLI',
    'CGEDHFIK',
    'CGJDHFEI',
    'HJBFIGLK',
    'EJIBHGLK',
    'EJBFIHLK',
    'EJBFIGLK',
    'EJBFHGLK',
    'EGBFIHLK',
    'EJBFHGLI',
    'EJBFHGIK',
    'HJBDIGLK',
    'HJBDIFLK',
    'IGBDJFLK',
    'HGBDJFLK',
    'HGBDIFLK',
    'HGBDJFLI',
    'HGBDJFIK',
    'EJBDIHLK',
    'EJBDIGLK',
    'EJBDHGLK',
    'EGBDIHLK',
    'EJBDHGLI',
    'EJBDHGIK',
    'EJBDIFLK',
    'EJBDHFLK',
    'EIBDHFLK',
    'EJBDHFLI',
    'EJBDHFIK',
    'EGBDJFLK',
    'EGBDIFLK',
    'EGBDJFLI',
    'EGBDJFIK',
    'EGBDHFLK',
    'HGBDJFLE',
    'HGBDJFEK',
    'EGBDHFLI',
    'EGBDHFIK',
    'HGBDJFEI',
    'HJBCIGLK',
    'HJBCIFLK',
    'IGBCJFLK',
    'HGBCJFLK',
    'HGBCIFLK',
    'HGBCJFLI',
    'HGBCJFIK',
    'EJBCIHLK',
    'EJBCIGLK',
    'EJBCHGLK',
    'EGBCIHLK',
    'EJBCHGLI',
    'EJBCHGIK',
    'EJBCIFLK',
    'EJBCHFLK',
    'EIBCHFLK',
    'EJBCHFLI',
    'EJBCHFIK',
    'EGBCJFLK',
    'EGBCIFLK',
    'EGBCJFLI',
    'EGBCJFIK',
    'EGBCHFLK',
    'HGBCJFLE',
    'HGBCJFEK',
    'EGBCHFLI',
    'EGBCHFIK',
    'HGBCJFEI',
    'HJBCIDLK',
    'IGBCJDLK',
    'HGBCJDLK',
    'HGBCIDLK',
    'HGBCJDLI',
    'HGBCJDIK',
    'CJBDIFLK',
    'CJBDHFLK',
    'CIBDHFLK',
    'CJBDHFLI',
    'CJBDHFIK',
    'CGBDJFLK',
    'CGBDIFLK',
    'CGBDJFLI',
    'CGBDJFIK',
    'CGBDHFLK',
    'CGBDHFLJ',
    'HGBCJFDK',
    'CGBDHFLI',
    'CGBDHFIK',
    'HGBCJFDI',
    'EJBCIDLK',
    'EJBCHDLK',
    'EIBCHDLK',
    'EJBCHDLI',
    'EJBCHDIK',
    'EGBCJDLK',
    'EGBCIDLK',
    'EGBCJDLI',
    'EGBCJDIK',
    'EGBCHDLK',
    'HGBCJDLE',
    'HGBCJDEK',
    'EGBCHDLI',
    'EGBCHDIK',
    'HGBCJDEI',
    'CJBDEFLK',
    'CEBDIFLK',
    'CJBDEFLI',
    'CJBDEFIK',
    'CEBDHFLK',
    'CJBDHFLE',
    'CJBDHFEK',
    'CEBDHFLI',
    'CEBDHFIK',
    'CJBDHFEI',
    'CGBDEFLK',
    'CGBDJFLE',
    'CGBDJFEK',
    'CGBDEFLI',
    'CGBDEFIK',
    'CGBDJFEI',
    'CGBDHFLE',
    'CGBDHFEK',
    'HGBCJFDE',
    'CGBDHFEI',
    'HJIFAGLK',
    'EJIAHGLK',
    'EJIFAHLK',
    'EJIFAGLK',
    'EGJFAHLK',
    'EGIFAHLK',
    'EGJFAHLI',
    'EGJFAHIK',
    'HJIDAGLK',
    'HJIDAFLK',
    'IGJDAFLK',
    'HGJDAFLK',
    'HGIDAFLK',
    'HGJDAFLI',
    'HGJDAFIK',
    'EJIDAHLK',
    'EJIDAGLK',
    'EGJDAHLK',
    'EGIDAHLK',
    'EGJDAHLI',
    'EGJDAHIK',
    'EJIDAFLK',
    'HJEDAFLK',
    'HEIDAFLK',
    'HJEDAFLI',
    'HJEDAFIK',
    'EGJDAFLK',
    'EGIDAFLK',
    'EGJDAFLI',
    'EGJDAFIK',
    'HGEDAFLK',
    'HGJDAFLE',
    'HGJDAFEK',
    'HGEDAFLI',
    'HGEDAFIK',
    'HGJDAFEI',
    'HJICAGLK',
    'HJICAFLK',
    'IGJCAFLK',
    'HGJCAFLK',
    'HGICAFLK',
    'HGJCAFLI',
    'HGJCAFIK',
    'EJICAHLK',
    'EJICAGLK',
    'EGJCAHLK',
    'EGICAHLK',
    'EGJCAHLI',
    'EGJCAHIK',
    'EJICAFLK',
    'HJECAFLK',
    'HEICAFLK',
    'HJECAFLI',
    'HJECAFIK',
    'EGJCAFLK',
    'EGICAFLK',
    'EGJCAFLI',
    'EGJCAFIK',
    'HGECAFLK',
    'HGJCAFLE',
    'HGJCAFEK',
    'HGECAFLI',
    'HGECAFIK',
    'HGJCAFEI',
    'HJICADLK',
    'IGJCADLK',
    'HGJCADLK',
    'HGICADLK',
    'HGJCADLI',
    'HGJCADIK',
    'CJIDAFLK',
    'HJFCADLK',
    'HFICADLK',
    'HJFCADLI',
    'HJFCADIK',
    'CGJDAFLK',
    'CGIDAFLK',
    'CGJDAFLI',
    'CGJDAFIK',
    'HGFCADLK',
    'CGJDAFLH',
    'HGJCAFDK',
    'HGFCADLI',
    'HGFCADIK',
    'HGJCAFDI',
    'EJICADLK',
    'HJECADLK',
    'HEICADLK',
    'HJECADLI',
    'HJECADIK',
    'EGJCADLK',
    'EGICADLK',
    'EGJCADLI',
    'EGJCADIK',
    'HGECADLK',
    'HGJCADLE',
    'HGJCADEK',
    'HGECADLI',
    'HGECADIK',
    'HGJCADEI',
    'CJEDAFLK',
    'CEIDAFLK',
    'CJEDAFLI',
    'CJEDAFIK',
    'HEFCADLK',
    'HJFCADLE',
    'HJECAFDK',
    'HEFCADLI',
    'HEFCADIK',
    'HJECAFDI',
    'CGEDAFLK',
    'CGJDAFLE',
    'CGJDAFEK',
    'CGEDAFLI',
    'CGEDAFIK',
    'CGJDAFEI',
    'HGFCADLE',
    'HGECAFDK',
    'HGJCAFDE',
    'HGECAFDI',
    'HJBAIGLK',
    'HJBAIFLK',
    'IJBFAGLK',
    'HJBFAGLK',
    'HGBAIFLK',
    'HJBFAGLI',
    'HJBFAGIK',
    'EJBAIHLK',
    'EJBAIGLK',
    'EJBAHGLK',
    'EGBAIHLK',
    'EJBAHGLI',
    'EJBAHGIK',
    'EJBAIFLK',
    'EJBFAHLK',
    'EIBFAHLK',
    'EJBFAHLI',
    'EJBFAHIK',
    'EJBFAGLK',
    'EGBAIFLK',
    'EJBFAGLI',
    'EJBFAGIK',
    'EGBFAHLK',
    'HJBFAGLE',
    'HJBFAGEK',
    'EGBFAHLI',
    'EGBFAHIK',
    'HJBFAGEI',
    'IJBDAHLK',
    'IJBDAGLK',
    'HJBDAGLK',
    'IGBDAHLK',
    'HJBDAGLI',
    'HJBDAGIK',
    'IJBDAFLK',
    'HJBDAFLK',
    'HIBDAFLK',
    'HJBDAFLI',
    'HJBDAFIK',
    'FJBDAGLK',
    'IGBDAFLK',
    'FJBDAGLI',
    'FJBDAGIK',
    'HGBDAFLK',
    'HGBDAFLJ',
    'HGBDAFJK',
    'HGBDAFLI',
    'HGBDAFIK',
    'HGBDAFIJ',
    'EJBAIDLK',
    'EJBDAHLK',
    'EIBDAHLK',
    'EJBDAHLI',
    'EJBDAHIK',
    'EJBDAGLK',
    'EGBAIDLK',
    'EJBDAGLI',
    'EJBDAGIK',
    'EGBDAHLK',
    'HJBDAGLE',
    'HJBDAGEK',
    'EGBDAHLI',
    'EGBDAHIK',
    'HJBDAGEI',
    'EJBDAFLK',
    'EIBDAFLK',
    'EJBDAFLI',
    'EJBDAFIK',
    'HEBDAFLK',
    'HJBDAFLE',
    'HJBDAFEK',
    'HEBDAFLI',
    'HEBDAFIK',
    'HJBDAFEI',
    'EGBDAFLK',
    'EGBDAFLJ',
    'EGBDAFJK',
    'EGBDAFLI',
    'EGBDAFIK',
    'EGBDAFIJ',
    'HGBDAFLE',
    'HGBDAFEK',
    'HGBDAFEJ',
    'HGBDAFEI',
    'IJBCAHLK',
    'IJBCAGLK',
    'HJBCAGLK',
    'IGBCAHLK',
    'HJBCAGLI',
    'HJBCAGIK',
    'IJBCAFLK',
    'HJBCAFLK',
    'HIBCAFLK',
    'HJBCAFLI',
    'HJBCAFIK',
    'CJBFAGLK',
    'IGBCAFLK',
    'CJBFAGLI',
    'CJBFAGIK',
    'HGBCAFLK',
    'HGBCAFLJ',
    'HGBCAFJK',
    'HGBCAFLI',
    'HGBCAFIK',
    'HGBCAFIJ',
    'EJBAICLK',
    'EJBCAHLK',
    'EIBCAHLK',
    'EJBCAHLI',
    'EJBCAHIK',
    'EJBCAGLK',
    'EGBAICLK',
    'EJBCAGLI',
    'EJBCAGIK',
    'EGBCAHLK',
    'HJBCAGLE',
    'HJBCAGEK',
    'EGBCAHLI',
    'EGBCAHIK',
    'HJBCAGEI',
    'EJBCAFLK',
    'EIBCAFLK',
    'EJBCAFLI',
    'EJBCAFIK',
    'HEBCAFLK',
    'HJBCAFLE',
    'HJBCAFEK',
    'HEBCAFLI',
    'HEBCAFIK',
    'HJBCAFEI',
    'EGBCAFLK',
    'EGBCAFLJ',
    'EGBCAFJK',
    'EGBCAFLI',
    'EGBCAFIK',
    'EGBCAFIJ',
    'HGBCAFLE',
    'HGBCAFEK',
    'HGBCAFEJ',
    'HGBCAFEI',
    'IJBCADLK',
    'HJBCADLK',
    'HIBCADLK',
    'HJBCADLI',
    'HJBCADIK',
    'CJBDAGLK',
    'IGBCADLK',
    'CJBDAGLI',
    'CJBDAGIK',
    'HGBCADLK',
    'HGBCADLJ',
    'HGBCADJK',
    'HGBCADLI',
    'HGBCADIK',
    'HGBCADIJ',
    'CJBDAFLK',
    'CIBDAFLK',
    'CJBDAFLI',
    'CJBDAFIK',
    'HFBCADLK',
    'CJBDAFLH',
    'HJBCAFDK',
    'HFBCADLI',
    'HFBCADIK',
    'HJBCAFDI',
    'CGBDAFLK',
    'CGBDAFLJ',
    'CGBDAFJK',
    'CGBDAFLI',
    'CGBDAFIK',
    'CGBDAFIJ',
    'CGBDAFLH',
    'HGBCAFDK',
    'HGBCAFDJ',
    'HGBCAFDI',
    'EJBCADLK',
    'EIBCADLK',
    'EJBCADLI',
    'EJBCADIK',
    'HEBCADLK',
    'HJBCADLE',
    'HJBCADEK',
    'HEBCADLI',
    'HEBCADIK',
    'HJBCADEI',
    'EGBCADLK',
    'EGBCADLJ',
    'EGBCADJK',
    'EGBCADLI',
    'EGBCADIK',
    'EGBCADIJ',
    'HGBCADLE',
    'HGBCADEK',
    'HGBCADEJ',
    'HGBCADEI',
    'CEBDAFLK',
    'CJBDAFLE',
    'CJBDAFEK',
    'CEBDAFLI',
    'CEBDAFIK',
    'CJBDAFEI',
    'HFBCADLE',
    'HEBCAFDK',
    'HJBCAFDE',
    'HEBCAFDI',
    'CGBDAFLE',
    'CGBDAFEK',
    'CGBDAFEJ',
    'CGBDAFEI',
    'HGBCAFDE',
)

ANNEX_C_BY_COMBINATION = {"".join(sorted(option)): option for option in ANNEX_C_OPTIONS}


@dataclass
class TeamStanding:
    team: str
    group: str
    played: int = 0
    points: int = 0
    goals_for: int = 0
    goals_against: int = 0

    @property
    def goal_difference(self):
        return self.goals_for - self.goals_against

    @property
    def sort_key(self):
        return (self.points, self.goal_difference, self.goals_for)


@dataclass
class WorldCupBracketUpdateSummary:
    updated_matches: int = 0
    pending_groups: list[str] = field(default_factory=list)
    unresolved_groups: list[str] = field(default_factory=list)
    third_place_ready: bool = False
    message: str = ""


def update_world_cup_bracket(commit=True):
    summaries = _group_summaries()
    group_positions = {}
    pending_groups = []
    unresolved_groups = []

    for group in GROUPS:
        standings, reason = _rank_group(group, summaries.get(group, []))
        if reason == "pending":
            pending_groups.append(group)
        elif reason == "unresolved":
            unresolved_groups.append(group)
        elif standings:
            group_positions[group] = standings

    updated = _update_fixed_round_of_32(group_positions)
    third_place_ready = False
    if len(group_positions) == len(GROUPS):
        third_groups = _best_third_groups(group_positions)
        if third_groups:
            third_place_ready = True
            updated += _update_third_place_round_of_32(group_positions, third_groups)

    updated += _update_knockout_advancement()

    if updated and commit:
        db.session.commit()

    summary = WorldCupBracketUpdateSummary(
        updated_matches=updated,
        pending_groups=pending_groups,
        unresolved_groups=unresolved_groups,
        third_place_ready=third_place_ready,
    )
    summary.message = _summary_message(summary)
    return summary


def _group_summaries():
    matches = (
        Match.query.filter_by(competition=WORLD_CUP_COMPETITION)
        .filter(Match.group_name.in_([f"Grupo {group}" for group in GROUPS]))
        .all()
    )
    summaries = {group: [] for group in GROUPS}
    for match in matches:
        group = match.group_name.replace("Grupo ", "").strip()
        if group in summaries:
            summaries[group].append(match)
    return summaries


def _rank_group(group, matches):
    finished = [match for match in matches if match.has_result]
    if len(finished) < GROUP_MATCHES_REQUIRED:
        return None, "pending"

    standings = {}
    for match in finished:
        home = standings.setdefault(match.home_team, TeamStanding(match.home_team, group))
        away = standings.setdefault(match.away_team, TeamStanding(match.away_team, group))
        home.played += 1
        away.played += 1
        home.goals_for += match.home_score
        home.goals_against += match.away_score
        away.goals_for += match.away_score
        away.goals_against += match.home_score
        if match.home_score > match.away_score:
            home.points += 3
        elif match.home_score < match.away_score:
            away.points += 3
        else:
            home.points += 1
            away.points += 1

    ranked = sorted(standings.values(), key=lambda standing: standing.sort_key, reverse=True)
    if _has_unresolved_tie(ranked, 0, 3):
        return None, "unresolved"
    return ranked, None


def _has_unresolved_tie(ranked, start_index, end_index):
    relevant = ranked[start_index : end_index + 1]
    keys = [standing.sort_key for standing in relevant]
    return len(keys) != len(set(keys))


def _best_third_groups(group_positions):
    thirds = [positions[2] for positions in group_positions.values()]
    ranked = sorted(thirds, key=lambda standing: standing.sort_key, reverse=True)
    if ranked[7].sort_key == ranked[8].sort_key:
        return None
    return "".join(sorted(standing.group for standing in ranked[:8]))


def _resolve_slot(slot, group_positions):
    rank = int(slot[0]) - 1
    group = slot[1]
    positions = group_positions.get(group)
    if not positions or len(positions) <= rank:
        return None
    return positions[rank].team


def _update_fixed_round_of_32(group_positions):
    updated = 0
    for api_id, (home_slot, away_slot) in FIXED_ROUND_OF_32_MATCHES.items():
        home_team = _resolve_slot(home_slot, group_positions)
        away_team = _resolve_slot(away_slot, group_positions)
        if home_team and away_team:
            updated += _set_match_teams(api_id, home_team, away_team)
    return updated


def _update_third_place_round_of_32(group_positions, third_groups):
    option = ANNEX_C_BY_COMBINATION.get(third_groups)
    if not option:
        return 0

    updated = 0
    for slot_group, third_group in zip(THIRD_PLACE_SLOTS, option):
        api_id = THIRD_PLACE_ROUND_OF_32_MATCHES[slot_group]
        home_team = _resolve_slot(f"1{slot_group}", group_positions)
        away_team = _resolve_slot(f"3{third_group}", group_positions)
        if home_team and away_team:
            updated += _set_match_teams(api_id, home_team, away_team)
    return updated


def _set_match_teams(api_id, home_team, away_team):
    match = Match.query.filter_by(api_id=api_id).first()
    if not match or not match.has_placeholder_teams:
        return 0
    if match.home_team == home_team and match.away_team == away_team:
        return 0
    match.home_team = home_team
    match.away_team = away_team
    return 1


def _update_knockout_advancement():
    updated = 0
    for target_api_id, (home_source, away_source) in KNOCKOUT_ADVANCEMENT_MATCHES.items():
        home_placeholder, away_placeholder = KNOCKOUT_TARGET_PLACEHOLDERS[target_api_id]
        home_team = _resolve_knockout_source(*home_source) or home_placeholder
        away_team = _resolve_knockout_source(*away_source) or away_placeholder
        updated += _set_knockout_match_teams(target_api_id, home_team, away_team)
    return updated


def _resolve_knockout_source(result_type, source_api_id):
    source_match = Match.query.filter_by(api_id=source_api_id).first()
    if not source_match or not source_match.has_result:
        return None

    winner = _knockout_winner(source_match)
    if not winner:
        return None
    if result_type == "winner":
        return winner
    return source_match.away_team if winner == source_match.home_team else source_match.home_team


def _knockout_winner(match):
    if match.home_score > match.away_score:
        return match.home_team
    if match.away_score > match.home_score:
        return match.away_team
    if match.winner_team in {match.home_team, match.away_team}:
        return match.winner_team
    return None


def _set_knockout_match_teams(api_id, home_team, away_team):
    match = Match.query.filter_by(api_id=api_id).first()
    if not match or match.has_result or match.status in {"live", "finished", "cancelled"}:
        return 0
    if not match.has_placeholder_teams and (match.home_team, match.away_team) == (home_team, away_team):
        return 0
    if not match.has_placeholder_teams and match.status != "scheduled":
        return 0
    if match.home_team == home_team and match.away_team == away_team:
        return 0
    match.home_team = home_team
    match.away_team = away_team
    if match.winner_team not in {None, home_team, away_team}:
        match.winner_team = None
    return 1


def _summary_message(summary):
    parts = [f"Cruces Mundial actualizados: {summary.updated_matches} cambios aplicados."]
    if summary.pending_groups:
        parts.append(f"Grupos pendientes: {', '.join(summary.pending_groups)}.")
    if summary.unresolved_groups:
        parts.append(f"Empates sin resolver por criterios disponibles: {', '.join(summary.unresolved_groups)}.")
    if not summary.third_place_ready:
        parts.append("Asignacion de mejores terceros pendiente.")
    return " ".join(parts)
