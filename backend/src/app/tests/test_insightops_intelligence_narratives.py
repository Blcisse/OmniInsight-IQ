import pytest

from src.app.intelligence.demo_profiles import (
    EXEC_STABLE_GROWTH,
    EXEC_REVENUE_RISK,
    EXEC_ENGAGEMENT_DROP,
    EXEC_ANOMALY_SPIKE,
)
from src.app.intelligence.narratives import build_executive_narrative
from src.app.intelligence.schemas import DriverAttribution, PrimaryDriver, PrioritizedInsight, SynthesisBlock
from src.app.services.insightops_intelligence import build_cross_domain_intelligence
from src.app.schemas.insightops_analytics import DeltaSummary, EngagementSummary, AnomalyResponse

pytestmark = pytest.mark.unit


def _base_inputs():
    kpi_summary = DeltaSummary(
        latest_value=100,
        previous_value=120,
        absolute_delta=-20,
        percent_delta=-0.166,
        rolling_avg_7d_latest=110,
    )
    engagement_summary = EngagementSummary(total=100, average_per_day=10, last_day_value=8, health_score=70)
    anomaly_summary = AnomalyResponse(org_id="demo", anomalies=[])
    return kpi_summary, engagement_summary, anomaly_summary


def test_demo_profiles_are_deterministic():
    profiles = [EXEC_STABLE_GROWTH, EXEC_REVENUE_RISK, EXEC_ENGAGEMENT_DROP, EXEC_ANOMALY_SPIKE]
    results = [p() for p in profiles]
    titles = [r["priorities"][0].title for r in results]
    assert len(set(titles)) == len(titles)
    # Repeat call yields same headline
    assert profiles[0]()["narrative"]["headline"] == results[0]["narrative"]["headline"]


def test_build_cross_domain_intelligence_explain_notes():
    kpi_summary, engagement_summary, anomaly_summary = _base_inputs()
    intel = build_cross_domain_intelligence(
        kpi_key="revenue",
        engagement_key="touches",
        kpi_summary=kpi_summary,
        engagement_summary=engagement_summary,
        anomaly_summary=anomaly_summary,
        explain=True,
    )
    assert intel["explainability_notes"]


def test_narrative_from_structs_is_stable():
    driver = DriverAttribution(primary_driver=PrimaryDriver.KPI_TREND, supporting_factors=["kpi"], confidence=0.8)
    priorities = [
        PrioritizedInsight(title="revenue vs touches", impact_score=80, urgency_score=70, confidence=0.7, explainability_notes=["kpi_delta=0.1"]),
    ]
    synth = SynthesisBlock(
        situation="revenue and touches reviewed with anomaly context",
        evidence="Driver: KPI_TREND (confidence 0.80)",
        risk="Potential headwinds detected on revenue",
        opportunity="Align engagement (touches) to reinforce revenue",
        recommended_focus="Reinforce KPI and engagement alignment",
    )
    narrative = build_executive_narrative(synthesis=synth, priorities=priorities, driver=driver)
    narrative_repeat = build_executive_narrative(synthesis=synth, priorities=priorities, driver=driver)
    assert narrative == narrative_repeat
    assert "headline" in narrative and "why_now" in narrative and "top_drivers" in narrative and "immediate_focus" in narrative
