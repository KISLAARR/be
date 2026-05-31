from zoneinfo import ZoneInfo
from datetime import datetime

def get_salon_time(salon_timezone: str = "Europe/Moscow") -> datetime:
    """Текущее время в часовом поясе салона."""
    return datetime.now(ZoneInfo(salon_timezone))

def localize_time(naive_dt: datetime, salon_timezone: str) -> datetime:
    """Привязать наивное время к часовому поясу салона."""
    return naive_dt.replace(tzinfo=ZoneInfo(salon_timezone))