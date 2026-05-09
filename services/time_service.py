from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from flask import current_app


def app_timezone():
    timezone_name = current_app.config.get("APP_TIMEZONE", "America/Bogota")
    try:
        return ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        return ZoneInfo("America/Bogota")


def local_naive_to_utc_naive(value):
    local_value = value.replace(tzinfo=app_timezone()) if value.tzinfo is None else value.astimezone(app_timezone())
    return local_value.astimezone(timezone.utc).replace(tzinfo=None)


def utc_naive_to_local(value):
    utc_value = value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)
    return utc_value.astimezone(app_timezone())


def parse_local_datetime(value):
    return local_naive_to_utc_naive(datetime.strptime(value, "%Y-%m-%dT%H:%M"))


def format_local_datetime(value, fmt="%d/%m/%Y %H:%M"):
    if not value:
        return ""
    return utc_naive_to_local(value).strftime(fmt)
