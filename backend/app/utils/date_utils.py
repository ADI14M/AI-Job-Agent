from datetime import datetime, timezone

def get_current_utc() -> datetime:
    """Returns the current UTC datetime."""
    return datetime.now(timezone.utc)

def format_date(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Formats a datetime object to string."""
    return dt.strftime(fmt) if dt else ""
