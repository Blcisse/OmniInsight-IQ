from __future__ import annotations

from typing import Iterable, List, Optional

from .schemas import DriverAttribution, PrimaryDriver, SignalCorrelation


class DriverAttributionEngine:
    """Deterministic driver attribution based on correlations."""

    anomaly_threshold = 0.6
    engagement_threshold = 0.55
    kpi_threshold = 0.5

    @classmethod
    def attribute(
        cls,
        correlations: Iterable[SignalCorrelation],
        kpi_trend_confidence: float = 0.0,
    ) -> DriverAttribution:
        correlations = list(correlations)
        factors: List[str] = []

        anomaly_corr: Optional[SignalCorrelation] = None
        engagement_corr: Optional[SignalCorrelation] = None

        for corr in correlations:
            if corr.anomaly_key and (anomaly_corr is None or corr.confidence > anomaly_corr.confidence):
                anomaly_corr = corr
            if corr.signal_key and (engagement_corr is None or abs(corr.correlation_score) > abs(engagement_corr.correlation_score)):
                engagement_corr = corr

        # Anomaly-driven if confidence meets threshold
        if anomaly_corr and anomaly_corr.confidence >= cls.anomaly_threshold:
            factors.append(f"Anomaly correlation {anomaly_corr.anomaly_key} @ {anomaly_corr.confidence:.2f}")
            return DriverAttribution(
                primary_driver=PrimaryDriver.ANOMALY,
                supporting_factors=factors,
                confidence=anomaly_corr.confidence,
            )

        # Engagement-driven if strong correlation
        if engagement_corr and abs(engagement_corr.correlation_score) >= cls.engagement_threshold:
            factors.append(
                f"Engagement correlation {engagement_corr.signal_key} @ {abs(engagement_corr.correlation_score):.2f}"
            )
            return DriverAttribution(
                primary_driver=PrimaryDriver.ENGAGEMENT,
                supporting_factors=factors,
                confidence=min(max(engagement_corr.confidence, 0.0), 1.0),
            )

        # KPI trend dominant
        if kpi_trend_confidence >= cls.kpi_threshold:
            factors.append(f"KPI trend confidence {kpi_trend_confidence:.2f}")
            return DriverAttribution(
                primary_driver=PrimaryDriver.KPI_TREND,
                supporting_factors=factors,
                confidence=min(max(kpi_trend_confidence, 0.0), 1.0),
            )

        factors.append("No dominant driver detected")
        return DriverAttribution(primary_driver=PrimaryDriver.UNKNOWN, supporting_factors=factors, confidence=0.3)
