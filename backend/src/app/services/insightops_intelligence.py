from __future__ import annotations

from typing import Dict, List, Optional

from ..intelligence import correlate_signals
from ..intelligence.drivers import DriverAttributionEngine
from ..intelligence.priority import Prioritizer
from ..intelligence.synthesis import Synthesizer
from ..intelligence.schemas import DriverAttribution, PrioritizedInsight, SignalCorrelation, SynthesisBlock
from ..intelligence.narratives import build_executive_narrative
from ..intelligence.demo_profiles import (
    EXEC_STABLE_GROWTH,
    EXEC_REVENUE_RISK,
    EXEC_ENGAGEMENT_DROP,
    EXEC_ANOMALY_SPIKE,
)
from ..schemas.insightops_analytics import AnomalyResponse, DeltaSummary, EngagementSummary


def _engagement_percent_delta(summary: EngagementSummary) -> float:
    if summary.average_per_day and summary.average_per_day != 0 and summary.last_day_value is not None:
        return (summary.last_day_value - summary.average_per_day) / summary.average_per_day
    return 0.0


def build_cross_domain_intelligence(
    *,
    kpi_key: str,
    engagement_key: str,
    kpi_summary: DeltaSummary,
    engagement_summary: EngagementSummary,
    anomaly_summary: AnomalyResponse,
    demo_profile: Optional[str] = None,
    explain: bool = False,
) -> Dict[str, object]:
    # Demo presets short-circuit to deterministic outputs
    if demo_profile:
        profile_map = {
            "EXEC_STABLE_GROWTH": EXEC_STABLE_GROWTH,
            "EXEC_REVENUE_RISK": EXEC_REVENUE_RISK,
            "EXEC_ENGAGEMENT_DROP": EXEC_ENGAGEMENT_DROP,
            "EXEC_ANOMALY_SPIKE": EXEC_ANOMALY_SPIKE,
        }
        if demo_profile in profile_map:
            return profile_map[demo_profile]()

    kpi_percent_delta = kpi_summary.percent_delta or 0.0
    engagement_delta = _engagement_percent_delta(engagement_summary)
    anomalies_present = [a.type for a in anomaly_summary.anomalies]

    correlations: List[SignalCorrelation] = correlate_signals(
        kpi_key=kpi_key,
        engagement_signal_key=engagement_key,
        kpi_percent_delta=kpi_percent_delta,
        engagement_percent_delta=engagement_delta,
        anomaly_flags=anomalies_present,
        anomaly_key=anomalies_present[0] if anomalies_present else None,
        volatility_score=abs(kpi_percent_delta),
    )

    driver: DriverAttribution = DriverAttributionEngine.attribute(
        correlations=correlations,
        kpi_trend_confidence=min(1.0, abs(kpi_percent_delta)),
    )

    priorities: List[PrioritizedInsight] = Prioritizer.score(
        kpi_percent_delta=kpi_percent_delta,
        anomalies_present=bool(anomalies_present),
        trend_acceleration=abs(kpi_percent_delta),
        titles=[f"{kpi_key} movement vs {engagement_key}", "Anomaly context"],
    )

    synthesis: SynthesisBlock = Synthesizer.build(
        driver=driver,
        priorities=priorities,
        kpi_key=kpi_key,
        signal_key=engagement_key,
    )

    return {
        "correlations": correlations,
        "driver": driver,
        "priorities": priorities,
        "synthesis": synthesis,
        "narrative": build_executive_narrative(
            synthesis=synthesis,
            priorities=priorities,
            driver=driver,
        ),
        "executive_narrative": build_executive_narrative(
            synthesis=synthesis,
            priorities=priorities,
            driver=driver,
        ),
        "explainability_notes": priorities[0].explainability_notes if (explain and priorities) else [],
    }
