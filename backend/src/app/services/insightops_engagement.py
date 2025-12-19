from __future__ import annotations

from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from .insightops_analytics import (
    ALLOWED_SIGNAL_KEYS,
    DEFAULT_LOOKBACK_DAYS,
    DEFAULT_ORG_ID,
    default_window,
    fetch_signal_series,
    parse_date,
)
from ..schemas.insightops_analytics import EngagementSummary, SeriesPoint, SeriesResponse


async def get_signal_series(
    db: AsyncSession,
    org_id: str = DEFAULT_ORG_ID,
    signal_key: str = "touches",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    lookback_days: int = DEFAULT_LOOKBACK_DAYS,
) -> SeriesResponse:
    if signal_key not in ALLOWED_SIGNAL_KEYS:
        raise ValueError(f"Unsupported signal_key '{signal_key}'. Allowed: {sorted(ALLOWED_SIGNAL_KEYS)}")

    parsed_start = parse_date(start_date)
    parsed_end = parse_date(end_date)
    if parsed_start is None:
        window_start, window_end = default_window(parsed_end, lookback_days)
    else:
        window_start = parsed_start
        window_end = parsed_end or parsed_start

    rows = await fetch_signal_series(
        db=db,
        org_id=org_id,
        signal_key=signal_key,
        start_date=window_start,
        end_date=window_end,
    )

    points = [SeriesPoint(date=row["date"], value=float(row["value"])) for row in rows]
    return SeriesResponse(org_id=org_id, key=signal_key, start_date=window_start, end_date=window_end, points=points)


def aggregate_signals(points: List[SeriesPoint]) -> EngagementSummary:
    if not points:
        return EngagementSummary(total=0.0, average_per_day=0.0, last_day_value=None, health_score=0.0)

    total = sum(p.value for p in points)
    avg = total / len(points)
    last = points[-1].value

    return EngagementSummary(
        total=total,
        average_per_day=avg,
        last_day_value=last,
        health_score=0.0,  # set by compute_engagement_health
    )


def compute_engagement_health(points: List[SeriesPoint]) -> float:
    """Return a deterministic 0-100 health score based on last value vs baseline average."""
    if not points:
        return 0.0

    totals = aggregate_signals(points)
    baseline = totals.average_per_day
    last_value = totals.last_day_value

    if baseline <= 0 or last_value is None:
        return 0.0

    ratio = last_value / baseline

    if ratio >= 1:
        score = 85.0
    elif ratio >= 0.7:
        score = 55.0
    else:
        score = 25.0

    return max(0.0, min(100.0, score))
