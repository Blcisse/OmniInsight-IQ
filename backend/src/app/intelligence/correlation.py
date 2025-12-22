from __future__ import annotations

from typing import Iterable, List, Optional

from .schemas import SignalCorrelation


def _direction(delta: Optional[float], threshold: float = 0.01) -> str:
    if delta is None:
        return "flat"
    if delta > threshold:
        return "up"
    if delta < -threshold:
        return "down"
    return "flat"


def _is_volatile(volatility_score: Optional[float], volatility_flag: Optional[bool] = None) -> bool:
    if volatility_flag is not None:
        return bool(volatility_flag)
    if volatility_score is None:
        return False
    return volatility_score >= 0.5


def correlate_signals(
    *,
    kpi_key: str = "revenue",
    kpi_percent_delta: Optional[float] = None,
    engagement_percent_delta: Optional[float] = None,
    anomaly_flags: Optional[Iterable[str]] = None,
    volatility_score: Optional[float] = None,
    volatility_flag: Optional[bool] = None,
    engagement_signal_key: str = "touches",
    anomaly_key: Optional[str] = None,
) -> List[SignalCorrelation]:
    """
    Correlate KPI and engagement movements with anomaly context using simple deterministic rules.

    Inputs are deltas/flags already normalized by upstream analytics; no statistical libraries are used.
    """
    correlations: List[SignalCorrelation] = []
    anomalies_present = list(anomaly_flags or [])

    kpi_dir = _direction(kpi_percent_delta)
    engagement_dir = _direction(engagement_percent_delta)
    is_volatile = _is_volatile(volatility_score, volatility_flag)

    # KPI and engagement move together -> positive correlation
    if kpi_dir == "down" and engagement_dir == "down":
        correlations.append(
            SignalCorrelation(
                kpi_key=kpi_key,
                signal_key=engagement_signal_key,
                correlation_score=0.7,
                confidence=0.65,
            )
        )
    elif kpi_dir == "up" and engagement_dir == "up":
        correlations.append(
            SignalCorrelation(
                kpi_key=kpi_key,
                signal_key=engagement_signal_key,
                correlation_score=0.6,
                confidence=0.6,
            )
        )

    # Divergence between KPI and engagement -> negative relationship
    if (kpi_dir == "down" and engagement_dir == "up") or (kpi_dir == "up" and engagement_dir == "down"):
        correlations.append(
            SignalCorrelation(
                kpi_key=kpi_key,
                signal_key=engagement_signal_key,
                correlation_score=-0.6,
                confidence=0.6,
            )
        )

    # Volatility plus anomaly spike -> anomaly-driven correlation
    if is_volatile and anomalies_present:
        correlations.append(
            SignalCorrelation(
                kpi_key=kpi_key,
                anomaly_key=anomaly_key or anomalies_present[0],
                correlation_score=0.5,
                confidence=0.55,
            )
        )

    # If nothing matched, still return an empty list to keep consumers deterministic.
    return correlations
