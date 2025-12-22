from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.insightops_executive_brief import (
    ExecutiveBriefResponse,
    ExecutiveInsight,
    ExecutiveOpportunity,
    ExecutiveRisk,
)
from ..intelligence.schemas import DriverAttribution, PrioritizedInsight, SynthesisBlock
from .insightops_intelligence import build_cross_domain_intelligence
from .insightops import get_anomalies, get_engagement_summary, get_kpi_summary
from .insightops_interpretation.anomaly_interpreter import interpret_anomalies
from .insightops_interpretation.engagement_interpreter import interpret_engagement
from .insightops_interpretation.kpi_interpreter import interpret_kpi
from .insightops_interpretation.scoring import compute_priority_score


DEFAULT_METRIC_KEYS = ["revenue", "pipeline", "win_rate"]
DEFAULT_SIGNAL_KEYS = ["touches"]


async def build_executive_brief(
    db: AsyncSession,
    org_id: str = "demo_org",
    window_days: int = 14,
    metric_keys: Optional[List[str]] = None,
    signal_keys: Optional[List[str]] = None,
) -> ExecutiveBriefResponse:
    metric_keys = metric_keys or DEFAULT_METRIC_KEYS
    signal_keys = signal_keys or DEFAULT_SIGNAL_KEYS

    insights: list[ExecutiveInsight] = []
    risks: list[ExecutiveRisk] = []
    opportunities: list[ExecutiveOpportunity] = []
    notes: list[str] = []
    driver_attribution: DriverAttribution | None = None
    prioritized_insights: list[PrioritizedInsight] | None = None
    synthesis_block: SynthesisBlock | None = None

    kpi_interps: list[dict] = []
    primary_kpi_summary = None
    kpi_severity_max = 0

    # KPI insights and risks
    for metric_key in metric_keys:
        summary = await get_kpi_summary(
            db=db,
            org_id=org_id,
            metric_key=metric_key,
            lookback_days=window_days,
        )
        interpretation = interpret_kpi(
            summary.latest_value,
            summary.previous_value,
            summary.percent_delta,
            summary.rolling_avg_7d_latest,
        )
        if primary_kpi_summary is None:
            primary_kpi_summary = summary
        kpi_interps.append({"key": metric_key, "interpretation": interpretation})
        kpi_severity_max = max(kpi_severity_max, interpretation["severity"])

        insights.append(
            ExecutiveInsight(
                title=f"{metric_key.replace('_', ' ').title()} trend",
                summary=interpretation["message"],
                severity=interpretation["severity"],
                category="kpi",
            )
        )

        if interpretation["trend"] == "declining":
            risks.append(
                ExecutiveRisk(
                    title=f"{metric_key.replace('_', ' ').title()} decline",
                    description="Observed decline against recent baseline.",
                    severity=interpretation["severity"],
                )
            )

        if summary.latest_value is None:
            notes.append(f"No KPI data available for {metric_key} in the selected window.")

    # Engagement insight and risk from the first signal (signals are minimal for CD5)
    signal_key = signal_keys[0] if signal_keys else "touches"
    engagement_summary = await get_engagement_summary(
        db=db,
        org_id=org_id,
        signal_key=signal_key,
        lookback_days=window_days,
    )
    engagement_interpretation = interpret_engagement(
        engagement_summary.health_score,
        engagement_summary.average_per_day,
        engagement_summary.last_day_value,
    )
    engagement_severity = engagement_interpretation["severity"]

    insights.append(
        ExecutiveInsight(
            title=f"{signal_key.replace('_', ' ').title()} engagement",
            summary=engagement_interpretation["message"],
            severity=engagement_interpretation["severity"],
            category="engagement",
        )
    )

    has_recent_engagement = (engagement_summary.average_per_day or 0) > 0 or engagement_summary.last_day_value is not None
    if engagement_interpretation["status"] == "critical" and has_recent_engagement:
        risks.append(
            ExecutiveRisk(
                title=f"{signal_key.replace('_', ' ').title()} engagement at risk",
                description="Engagement health is critical compared to the recent window.",
                severity=engagement_interpretation["severity"],
            )
        )

    # Anomalies insight and risk (revenue focus by default)
    anomalies_response = await get_anomalies(
        db=db,
        org_id=org_id,
        metric_key="revenue",
        signal_key=None,
        lookback_days=window_days,
    )
    anomaly_interpretation = interpret_anomalies(anomalies_response.anomalies)
    anomaly_severity = anomaly_interpretation["severity"]

    insights.append(
        ExecutiveInsight(
            title="Anomaly scan",
            summary=anomaly_interpretation["message"],
            severity=anomaly_interpretation["severity"],
            category="anomaly",
        )
    )

    if anomalies_response.anomalies:
        risks.append(
            ExecutiveRisk(
                title="Anomalies detected",
                description=anomaly_interpretation["message"],
                severity=anomaly_interpretation["severity"],
            )
        )

    # Opportunities (deterministic rule)
    has_improving_kpi = any(item["interpretation"]["trend"] == "improving" for item in kpi_interps)
    if has_improving_kpi and engagement_interpretation["status"] == "healthy":
        opportunities.append(
            ExecutiveOpportunity(
                title="Growth momentum",
                description="Improving KPI trend paired with healthy engagement suggests expansion runway.",
                confidence=75,
            )
        )

    # Clamp collection sizes to requested bounds
    insights = insights[:5]
    risks = risks[:3]
    opportunities = opportunities[:2]

    # Priority score aggregation
    priority = compute_priority_score(
        kpi_sev=kpi_severity_max,
        engagement_sev=engagement_severity,
        anomaly_sev=anomaly_severity,
    )

    if not anomalies_response.anomalies:
        notes.append("No anomalies detected in the selected window.")
    if not opportunities:
        notes.append("Opportunities limited due to insufficient positive signals.")

    # Cross-domain intelligence (optional enrichment, deterministic and DB-free)
    try:
        intelligence = build_cross_domain_intelligence(
            kpi_key=metric_keys[0],
            engagement_key=signal_key,
            kpi_summary=primary_kpi_summary or summary,
            engagement_summary=engagement_summary,
            anomaly_summary=anomalies_response,
            explain=True,
        )
        driver_attribution = intelligence["driver"]
        prioritized_insights = intelligence["priorities"]
        synthesis_block = intelligence["synthesis"]
        executive_narrative = intelligence.get("executive_narrative")
        top_drivers = executive_narrative.get("top_drivers") if executive_narrative else None
        priority_focus = executive_narrative.get("immediate_focus") if executive_narrative else None
    except Exception:
        # Keep backwards compatibility if enrichment fails
        driver_attribution = None
        prioritized_insights = None
        synthesis_block = None
        executive_narrative = None
        top_drivers = None
        priority_focus = None

    return ExecutiveBriefResponse(
        org_id=org_id,
        generated_at=datetime.utcnow(),
        window_days=window_days,
        priority_score=priority["priority_score"],
        priority_level=priority["level"],
        insights=insights,
        risks=risks,
        opportunities=opportunities,
        notes=notes,
        driver_attribution=driver_attribution,
        prioritized_insights=prioritized_insights,
        synthesis_block=synthesis_block,
        executive_narrative=executive_narrative,
        top_drivers=top_drivers,
        priority_focus=priority_focus,
    )
