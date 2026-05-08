import csv
import os
from functools import lru_cache


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEAM_FLAGS_CSV = os.path.join(BASE_DIR, "data", "team_flags.csv")
PLACEHOLDER_TERMS = ("Clasificado", "Ganador", "Perdedor")


@lru_cache(maxsize=1)
def load_team_flags():
    flags = {}
    with open(TEAM_FLAGS_CSV, encoding="utf-8-sig", newline="") as flags_file:
        for row in csv.DictReader(flags_file):
            team = row.get("team", "").strip()
            if team:
                flags[team] = {
                    "code": row.get("flag_code", "").strip(),
                    "url": row.get("flag_url", "").strip(),
                    "svg_url": row.get("flag_svg_url", "").strip(),
                }
    return flags


def is_placeholder_team(team_name):
    return not team_name or any(term in team_name for term in PLACEHOLDER_TERMS)


def team_flag(team_name):
    if is_placeholder_team(team_name):
        return None
    return load_team_flags().get(team_name)


def team_flag_fallback(team_name):
    return "🏆" if is_placeholder_team(team_name) else "🏳️"
