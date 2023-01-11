from datetime import datetime, timezone


def is_tz_aware(d: datetime) -> bool:
    return d.tzinfo is not None and d.tzinfo.utcoffset(d) is not None


def must_be_tz_aware(d: datetime):
    """
    If d is not timezone aware, raise a ValueError.
    """
    if not is_tz_aware(d):
        raise ValueError("datetime must be timezone aware")


def utcnow() -> datetime:
    """
    Get a timezone-aware datetime for now, set to UTC.
    """
    return datetime.now(timezone.utc)
