from src.app.services.insightops_interpretation.anomaly_interpreter import interpret_anomalies
from src.app.services.insightops_interpretation.engagement_interpreter import interpret_engagement
from src.app.services.insightops_interpretation.kpi_interpreter import interpret_kpi
from src.app.services.insightops_interpretation.scoring import compute_priority_score


def test_kpi_interpretation_declining_stable_improving():
    declining = interpret_kpi(latest=90, previous=100, percent_delta=-6.0, rolling_avg_7d=95)
    assert declining["trend"] == "declining"
    assert declining["severity"] == 70
    assert declining["message"] == "Performance declining (-6.0% vs prior period)."

    stable = interpret_kpi(latest=100, previous=99, percent_delta=0.0, rolling_avg_7d=100)
    assert stable["trend"] == "stable"
    assert stable["severity"] == 40
    assert stable["message"] == "Performance stable within ±5% of the prior period."

    improving = interpret_kpi(latest=110, previous=100, percent_delta=6.0, rolling_avg_7d=105)
    assert improving["trend"] == "improving"
    assert improving["severity"] == 10
    assert improving["message"] == "Performance improving (6.0% vs prior period)."


def test_engagement_interpretation_health_watch_critical():
    healthy = interpret_engagement(health_score=85, avg_per_day=12, last_day_value=15)
    assert healthy["status"] == "healthy"
    assert healthy["severity"] == 10
    assert healthy["message"] == "Engagement is healthy with strong recent activity."

    watch = interpret_engagement(health_score=55, avg_per_day=8, last_day_value=6)
    assert watch["status"] == "watch"
    assert watch["severity"] == 40
    assert watch["message"] == "Engagement is steady but should be monitored for softening."

    critical = interpret_engagement(health_score=20, avg_per_day=2, last_day_value=1)
    assert critical["status"] == "critical"
    assert critical["severity"] == 80
    assert critical["message"] == "Engagement is low; immediate action recommended."


def test_anomaly_interpretation_empty_vs_present():
    none = interpret_anomalies([])
    assert none["risk"] == "none"
    assert none["count"] == 0
    assert none["severity"] == 0
    assert none["message"] == "No anomalies detected."

    present = interpret_anomalies(
        [{"type": "kpi_spike", "severity": "critical", "description": "Spiked", "date": "2024-01-01"}]
    )
    assert present["risk"] == "present"
    assert present["count"] == 1
    assert present["severity"] == 90
    assert present["message"] == "1 anomaly detected."


def test_priority_score_levels():
    low = compute_priority_score(kpi_sev=10, engagement_sev=10, anomaly_sev=10)
    assert low == {"priority_score": 10, "level": "low"}

    medium = compute_priority_score(kpi_sev=80, engagement_sev=60, anomaly_sev=50)
    assert medium == {"priority_score": 68, "level": "medium"}

    high = compute_priority_score(kpi_sev=100, engagement_sev=100, anomaly_sev=100)
    assert high == {"priority_score": 100, "level": "high"}
import pytest

pytestmark = pytest.mark.unit
