from __future__ import annotations

from datetime import date, timedelta


def parse_date(value: str | None) -> date | None:
    """Parse an ISO date string (YYYY-MM-DD) into a `date` or return None."""
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("Invalid date format. Use YYYY-MM-DD.") from exc


def default_window(end_date: date | None, lookback_days: int) -> tuple[date, date]:
    """
    Compute a default date window ending at `end_date` (or today) and looking
    back `lookback_days`.
    """
    if lookback_days <= 0:
        raise ValueError("lookback_days must be positive")

    effective_end = end_date or date.today()
    start_date = effective_end - timedelta(days=lookback_days)

    if start_date > effective_end:
        raise ValueError("start_date cannot be after end_date")

    return start_date, effective_end
