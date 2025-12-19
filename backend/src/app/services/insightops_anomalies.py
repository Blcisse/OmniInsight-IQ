from __future__ import annotations

from datetime import date
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from .insightops_analytics import (
    ALLOWED_KPI_KEYS,
    ALLOWED_SIGNAL_KEYS,
    DEFAULT_LOOKBACK_DAYS,
    DEFAULT_ORG_ID,
    MetricSeriesPoint,
    default_window,
    fetch_kpi_series,
    fetch_signal_series,
    parse_date,
)

# Thresholds
SPIKE_THRESHOLD_PCT = 0.30  # 30% deviation
KPI_GAP_THRESHOLD_DAYS = 2
FLATLINE_DAYS = 3
COLLAPSE_THRESHOLD_PCT = 0.50  # 50% drop vs prior window


async def _load_points(
    db: AsyncSession,
    org_id: str,
    key: str,
    start_date: Optional[str],
    end_date: Optional[str],
    lookback_days: int,
    fetcher,
) -> List[MetricSeriesPoint]:
    parsed_start = parse_date(start_date)
    parsed_end = parse_date(end_date)
    if parsed_start is None:
        window_start, window_end = default_window(parsed_end, lookback_days)
    else:
        window_start = parsed_start
        window_end = parsed_end or parsed_start

    rows = await fetcher(
        db=db,
        org_id=org_id,
        start_date=window_start,
        end_date=window_end,
        metric_key=key if fetcher is fetch_kpi_series else None,
        signal_key=key if fetcher is fetch_signal_series else None,
    )
    return [MetricSeriesPoint(date=row["date"], value=float(row["value"])) for row in rows]


def _maybe_add_spike_anomaly(anomalies: List[dict], points: List[MetricSeriesPoint]) -> None:
    if len(points) < 2:
        return
    baseline_points = points[:-1]
    latest = points[-1].value
    baseline_avg = sum(p.value for p in baseline_points) / len(baseline_points) if baseline_points else None
    if not baseline_avg or baseline_avg == 0:
        return

    deviation = (latest - baseline_avg) / baseline_avg
    if abs(deviation) >= SPIKE_THRESHOLD_PCT:
        severity = "critical" if abs(deviation) >= SPIKE_THRESHOLD_PCT * 2 else "warning"
        direction = "spike" if deviation > 0 else "drop"
        anomalies.append(
            {
                "type": f"kpi_{direction}",
                "severity": severity,
                "description": f"{direction.capitalize()} of {deviation*100:.1f}% vs rolling baseline",
                "date": points[-1].date,
            }
        )


def _maybe_add_gap_anomaly(anomalies: List[dict], points: List[MetricSeriesPoint]) -> None:
    for prev, curr in zip(points, points[1:]):
        gap = (curr.date - prev.date).days
        if gap > KPI_GAP_THRESHOLD_DAYS:
            anomalies.append(
                {
                    "type": "kpi_missing_data",
                    "severity": "warning",
                    "description": f"Gap of {gap} days between {prev.date} and {curr.date}",
                    "date": curr.date,
                }
            )


def compute_kpi_anomalies(points: List[MetricSeriesPoint]) -> List[dict]:
    anomalies: List[dict] = []
    if not points:
        return anomalies
    _maybe_add_spike_anomaly(anomalies, points)
    _maybe_add_gap_anomaly(anomalies, points)
    return anomalies


def compute_engagement_anomalies(points: List[MetricSeriesPoint]) -> List[dict]:
    anomalies: List[dict] = []
    if not points:
        return anomalies

    # Flatline: last N days all zero
    tail = points[-FLATLINE_DAYS:] if len(points) >= FLATLINE_DAYS else points
    if len(tail) >= FLATLINE_DAYS and all(p.value == 0 for p in tail):
        anomalies.append(
            {
                "type": "engagement_flatline",
                "severity": "critical",
                "description": f"Zero activity for {FLATLINE_DAYS} consecutive days",
                "date": tail[-1].date,
            }
        )

    # Sudden collapse: last value < 50% of prior average
    if len(points) >= 2:
        baseline_points = points[:-1]
        baseline_avg = sum(p.value for p in baseline_points) / len(baseline_points) if baseline_points else None
        last_value = points[-1].value
        if baseline_avg and baseline_avg > 0 and last_value <= baseline_avg * (1 - COLLAPSE_THRESHOLD_PCT):
            severity = "critical" if last_value == 0 else "warning"
            drop_pct = ((baseline_avg - last_value) / baseline_avg) * 100
            anomalies.append(
                {
                    "type": "engagement_collapse",
                    "severity": severity,
                    "description": f"Drop of {drop_pct:.1f}% vs prior average",
                    "date": points[-1].date,
                }
            )

    return anomalies


async def get_anomalies(
    db: AsyncSession,
    org_id: str = DEFAULT_ORG_ID,
    metric_key: Optional[str] = None,
    signal_key: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    lookback_days: int = DEFAULT_LOOKBACK_DAYS,
) -> List[dict]:
    if metric_key and signal_key:
        raise ValueError("Provide either metric_key or signal_key, not both.")
    if metric_key:
        if metric_key not in ALLOWED_KPI_KEYS:
            raise ValueError(f"Unsupported metric_key '{metric_key}'. Allowed: {sorted(ALLOWED_KPI_KEYS)}")
        points = await _load_points(
            db=db,
            org_id=org_id,
            key=metric_key,
            start_date=start_date,
            end_date=end_date,
            lookback_days=lookback_days,
            fetcher=fetch_kpi_series,
        )
        return compute_kpi_anomalies(points)
    if signal_key:
        if signal_key not in ALLOWED_SIGNAL_KEYS:
            raise ValueError(f"Unsupported signal_key '{signal_key}'. Allowed: {sorted(ALLOWED_SIGNAL_KEYS)}")
        points = await _load_points(
            db=db,
            org_id=org_id,
            key=signal_key,
            start_date=start_date,
            end_date=end_date,
            lookback_days=lookback_days,
            fetcher=fetch_signal_series,
        )
        return compute_engagement_anomalies(points)
    raise ValueError("metric_key or signal_key is required to compute anomalies.")
