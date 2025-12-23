from __future__ import annotations

from typing import List, Tuple

from .schemas import DriverAttribution, PrioritizedInsight, SynthesisBlock


def _headline(priorities: List[PrioritizedInsight], driver: DriverAttribution) -> str:
    if priorities:
        top = priorities[0]
        return f"{top.title}: impact {top.impact_score}/100, urgency {top.urgency_score}/100"
    return f"Driver: {driver.primary_driver.value}"


def _why_now(priorities: List[PrioritizedInsight]) -> str:
    if not priorities:
        return "No pressing movements detected."
    top = priorities[0]
    return f"Urgency {top.urgency_score}/100 driven by recent KPI movement; confidence {top.confidence:.2f}."


def _top_drivers(driver: DriverAttribution) -> List[str]:
    notes = list(driver.supporting_factors or [])
    if driver.primary_driver.value not in notes:
        notes.insert(0, f"Primary: {driver.primary_driver.value}")
    return notes[:3]


def _focus_recommendation(synthesis: SynthesisBlock) -> str:
    return synthesis.recommended_focus


def build_executive_narrative(
    *,
    synthesis: SynthesisBlock,
    priorities: List[PrioritizedInsight],
    driver: DriverAttribution,
) -> dict:
    """
    Deterministic executive-ready narrative built from structured intelligence.
    """
    return {
        "headline": _headline(priorities, driver),
        "why_now": _why_now(priorities),
        "top_drivers": _top_drivers(driver),
        "immediate_focus": _focus_recommendation(synthesis),
    }
