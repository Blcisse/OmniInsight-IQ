from __future__ import annotations

from typing import List

from .schemas import DriverAttribution, PrioritizedInsight, SynthesisBlock


class Synthesizer:
    """Produce deterministic narrative blocks without LLMs."""

    @staticmethod
    def build(
        *,
        driver: DriverAttribution,
        priorities: List[PrioritizedInsight],
        kpi_key: str = "revenue",
        signal_key: str = "touches",
    ) -> SynthesisBlock:
        top_priority = priorities[0] if priorities else None
        evidence_parts = [f"Driver: {driver.primary_driver.value} (confidence {driver.confidence:.2f})"]
        if driver.supporting_factors:
            evidence_parts.extend(driver.supporting_factors)

        risk = f"Potential headwinds detected on {kpi_key}" if top_priority and top_priority.urgency_score > 60 else "None observed"
        opportunity = (
            f"Align engagement ({signal_key}) to reinforce {kpi_key}"
            if top_priority and top_priority.impact_score > 50
            else "None highlighted"
        )

        focus = (
            "Stabilize anomalies and engagement first"
            if driver.primary_driver.value == "ANOMALY"
            else "Reinforce KPI and engagement alignment"
        )

        return SynthesisBlock(
            situation=f"{kpi_key} and {signal_key} reviewed with anomaly context",
            evidence="; ".join(evidence_parts),
            risk=risk,
            opportunity=opportunity,
            recommended_focus=focus,
        )
