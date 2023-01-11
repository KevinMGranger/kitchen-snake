from datetime import datetime


def must_be_tz_aware(d: datetime):
    # TODO: docs say yu need to check
    # the offset too, but why?
    if d.tzinfo is None:
        raise ValueError("datetime must be timezone aware")
