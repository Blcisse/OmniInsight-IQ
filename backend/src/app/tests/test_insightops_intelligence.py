import pytest

from datetime import date

from src.app.intelligence.correlation import correlate_signals
from src.app.intelligence.drivers import DriverAttributionEngine
from src.app.intelligence.priority import Prioritizer
from src.app.intelligence.synthesis import Synthesizer
from src.app.intelligence.schemas import PrimaryDriver, SignalCorrelation
from src.app.services.insightops_intelligence import build_cross_domain_intelligence
from src.app.schemas.insightops_analytics import Anomaly, AnomalyResponse, DeltaSummary, EngagementSummary


pytestmark = pytest.mark.unit


def test_correlation_positive_alignment():
    results = correlate_signals(
        kpi_key="revenue",
        kpi_percent_delta=-0.1,
        engagement_percent_delta=-0.05,
        anomaly_flags=[],
    )
    assert any(c.signal_key == "touches" and c.correlation_score > 0 for c in results)


def test_correlation_divergence():
    results = correlate_signals(
        kpi_key="revenue",
        kpi_percent_delta=-0.1,
        engagement_percent_delta=0.1,
        anomaly_flags=[],
    )
    assert any(c.correlation_score < 0 for c in results)


def test_driver_prefers_anomaly_when_confident():
    correlations = [
        SignalCorrelation(kpi_key="revenue", anomaly_key="spike", correlation_score=0.5, confidence=0.7)
    ]
    driver = DriverAttributionEngine.attribute(correlations=correlations, kpi_trend_confidence=0.2)
    assert driver.primary_driver == PrimaryDriver.ANOMALY


def test_priorities_sorted_and_scaled():
    priorities = Prioritizer.score(kpi_percent_delta=-0.2, anomalies_present=True, trend_acceleration=0.1, titles=["a", "b"])
    assert priorities[0].impact_score >= priorities[1].impact_score
    assert all(0 <= p.impact_score <= 100 for p in priorities)
    assert all(0 <= p.urgency_score <= 100 for p in priorities)
    assert all(p.explainability_notes for p in priorities)


def test_synthesis_uses_driver_and_priority():
    driver = DriverAttributionEngine.attribute(correlations=[], kpi_trend_confidence=0.6)
    priorities = Prioritizer.score(kpi_percent_delta=0.3, anomalies_present=False, trend_acceleration=0.1, titles=["impact"])
    block = Synthesizer.build(driver=driver, priorities=priorities, kpi_key="revenue", signal_key="touches")
    assert "revenue" in block.situation
    assert block.recommended_focus


def test_build_cross_domain_intelligence_end_to_end():
    kpi_summary = DeltaSummary(latest_value=100, previous_value=120, absolute_delta=-20, percent_delta=-0.166, rolling_avg_7d_latest=110)
    engagement_summary = EngagementSummary(total=100, average_per_day=10, last_day_value=8, health_score=70)
    anomaly_response = AnomalyResponse(org_id="demo", anomalies=[Anomaly(type="spike", severity="warning", description="test", date=date.today())])

    intelligence = build_cross_domain_intelligence(
        kpi_key="revenue",
        engagement_key="touches",
        kpi_summary=kpi_summary,
        engagement_summary=engagement_summary,
        anomaly_summary=anomaly_response,
    )

    assert intelligence["driver"] is not None
    assert intelligence["priorities"]
    assert intelligence["synthesis"] is not None
