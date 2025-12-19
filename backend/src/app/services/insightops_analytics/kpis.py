from __future__ import annotations

from datetime import date
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from .constants import ALLOWED_KPI_KEYS, DEFAULT_LOOKBACK_DAYS, DEFAULT_ORG_ID
from .db import fetch_kpi_series
from .time import default_window, parse_date
from ..schemas.insightops_analytics import DeltaSummary, SeriesPoint, SeriesResponse


async def get_kpi_series(
    db: AsyncSession,
    org_id: str = DEFAULT_ORG_ID,
    metric_key: str = "revenue",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    lookback_days: int = DEFAULT_LOOKBACK_DAYS,
) -> SeriesResponse:
    """Fetch KPI series for an org/metric with safe defaults."""
    if metric_key not in ALLOWED_KPI_KEYS:
        raise ValueError(f"Unsupported metric_key '{metric_key}'. Allowed: {sorted(ALLOWED_KPI_KEYS)}")

    parsed_start = parse_date(start_date)
    parsed_end = parse_date(end_date)
    if parsed_start is None:
        window_start, window_end = default_window(parsed_end, lookback_days)
    else:
        window_start = parsed_start
        window_end = parsed_end or parsed_start

    rows = await fetch_kpi_series(
        db=db,
        org_id=org_id,
        metric_key=metric_key,
        start_date=window_start,
        end_date=window_end,
    )

    points = [SeriesPoint(date=row["date"], value=float(row["value"])) for row in rows]
    return SeriesResponse(org_id=org_id, key=metric_key, start_date=window_start, end_date=window_end, points=points)


def compute_kpi_delta(points: List[SeriesPoint], rolling_avg_window: int = 7) -> DeltaSummary:
    """Compute latest vs previous deltas from a time-ordered series."""
    if not points:
        return DeltaSummary(
            latest_value=None,
            previous_value=None,
            absolute_delta=None,
            percent_delta=None,
            rolling_avg_7d_latest=None,
        )

    latest = points[-1].value
    previous = points[-2].value if len(points) >= 2 else None
    absolute_delta = latest - previous if previous is not None else None
    percent_delta = None
    if previous not in (None, 0):
        percent_delta = (absolute_delta / previous) * 100  # type: ignore[arg-type]

    rolling_avg = compute_rolling_average(points, window=rolling_avg_window)

    return DeltaSummary(
        latest_value=latest,
        previous_value=previous,
        absolute_delta=absolute_delta,
        percent_delta=percent_delta,
        rolling_avg_7d_latest=rolling_avg,
    )


def compute_rolling_average(points: List[SeriesPoint], window: int = 7) -> Optional[float]:
    """Return trailing average over the given window size."""
    if window <= 0:
        raise ValueError("window must be positive")
    if not points:
        return None
    window_points = points[-window:] if len(points) >= window else points
    return sum(p.value for p in window_points) / len(window_points)
