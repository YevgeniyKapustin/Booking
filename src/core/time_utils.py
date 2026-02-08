from datetime import date, datetime, time, timezone
from zoneinfo import ZoneInfo

from src.core.config import settings


def get_app_timezone() -> ZoneInfo:
    return ZoneInfo(settings.app_timezone)


def normalize_time(target_time: time) -> time:
    if target_time.tzinfo is None:
        return target_time
    return target_time.replace(tzinfo=None)


def combine_local(target_date: date, target_time: time) -> datetime:
    normalized_time = normalize_time(target_time)
    return datetime.combine(target_date, normalized_time, tzinfo=get_app_timezone())


def to_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
