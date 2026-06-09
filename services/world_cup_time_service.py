from datetime import datetime, timezone
from zoneinfo import ZoneInfo


VENUE_TIMEZONES = {
    "AT&T Stadium": "America/Chicago",
    "Arrowhead Stadium": "America/Chicago",
    "BC Place": "America/Vancouver",
    "BMO Field": "America/Toronto",
    "Estadio Akron": "America/Mexico_City",
    "Estadio Azteca": "America/Mexico_City",
    "Estadio BBVA": "America/Monterrey",
    "Gillette Stadium": "America/New_York",
    "Hard Rock Stadium": "America/New_York",
    "Levi's Stadium": "America/Los_Angeles",
    "Lincoln Financial Field": "America/New_York",
    "Lumen Field": "America/Los_Angeles",
    "Mercedes-Benz Stadium": "America/New_York",
    "MetLife Stadium": "America/New_York",
    "NRG Stadium": "America/Chicago",
    "SoFi Stadium": "America/Los_Angeles",
}


def world_cup_venue_local_to_utc_naive(date_value, time_value, venue):
    local_datetime = datetime.strptime(f"{date_value} {time_value}", "%Y-%m-%d %H:%M")
    timezone_name = next((name for stadium, name in VENUE_TIMEZONES.items() if stadium in venue), None)
    if timezone_name is None:
        raise ValueError(f"sede sin zona horaria configurada: {venue}")
    return local_datetime.replace(tzinfo=ZoneInfo(timezone_name)).astimezone(timezone.utc).replace(tzinfo=None)
