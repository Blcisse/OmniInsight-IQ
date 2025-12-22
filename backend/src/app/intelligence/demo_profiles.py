from __future__ import annotations

from typing import Dict

from .narratives import build_executive_narrative
from ..schemas.insightops_analytics import DeltaSummary, EngagementSummary, Anomaly, AnomalyResponse
def _build_intel_for_profile(kpi_percent_delta: float, engagement_percent_delta: float, anomalies: bool):
    from datetime import date
    from ..services import insightops_intelligence as _intel_service
    return _intel_service.build_cross_domain_intelligence(
        kpi_key="revenue",
        engagement_key="touches",
        kpi_summary=DeltaSummary(
            latest_value=100.0,
            previous_value=100.0 * (1 - kpi_percent_delta),
            absolute_delta=100.0 - 100.0 * (1 - kpi_percent_delta),
            percent_delta=kpi_percent_delta,
            rolling_avg_7d_latest=100.0,
        ),
        engagement_summary=EngagementSummary(
            total=100.0,
            average_per_day=10.0,
            last_day_value=10.0 * (1 + engagement_percent_delta),
            health_score=70.0,
        ),
            anomaly_summary=AnomalyResponse(
                org_id="demo_org",
                anomalies=[Anomaly(type="spike", severity="warning", description="synthetic", date=date.today())] if anomalies else [],
            ),
        )


def _base_intelligence(kpi_percent_delta: float, engagement_percent_delta: float, anomalies: bool):
    intel = _build_intel_for_profile(kpi_percent_delta, engagement_percent_delta, anomalies)
    narrative = build_executive_narrative(
        synthesis=intel["synthesis"],
        priorities=intel["priorities"],
        driver=intel["driver"],
    )
    return {**intel, "narrative": narrative}


def EXEC_STABLE_GROWTH() -> Dict[str, object]:
    intel = _base_intelligence(kpi_percent_delta=0.08, engagement_percent_delta=0.05, anomalies=False)
    intel["priorities"][0].title = "Stable growth"
    return intel


def EXEC_REVENUE_RISK() -> Dict[str, object]:
    intel = _base_intelligence(kpi_percent_delta=-0.12, engagement_percent_delta=-0.08, anomalies=True)
    intel["priorities"][0].title = "Revenue at risk"
    return intel


def EXEC_ENGAGEMENT_DROP() -> Dict[str, object]:
    intel = _base_intelligence(kpi_percent_delta=0.0, engagement_percent_delta=-0.15, anomalies=False)
    intel["priorities"][0].title = "Engagement drop"
    return intel


def EXEC_ANOMALY_SPIKE() -> Dict[str, object]:
    intel = _base_intelligence(kpi_percent_delta=-0.05, engagement_percent_delta=0.02, anomalies=True)
    intel["priorities"][0].title = "Anomaly spike"
    return intel
