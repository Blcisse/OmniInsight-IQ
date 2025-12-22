from __future__ import annotations

from typing import List

from .schemas import PrioritizedInsight


class Prioritizer:
    """Deterministic scoring based on KPI deltas, anomalies, and acceleration."""

    @staticmethod
    def _clamp(value: float, low: int = 0, high: int = 100) -> int:
        return int(max(low, min(high, round(value))))

    @classmethod
    def score(
        cls,
        *,
        kpi_percent_delta: float | None = None,
        anomalies_present: bool = False,
        trend_acceleration: float | None = None,
        titles: List[str] | None = None,
    ) -> List[PrioritizedInsight]:
        titles = titles or ["Cross-domain insight"]

        abs_delta = abs(kpi_percent_delta or 0.0)
        impact_score = cls._clamp(abs_delta * 100)

        accel = abs(trend_acceleration or 0.0)
        urgency_score = cls._clamp(30 + (20 if anomalies_present else 0) + accel * 50 + abs_delta * 30)

        base_conf = 0.7 if anomalies_present else 0.6

        insights: List[PrioritizedInsight] = []
        for idx, title in enumerate(titles):
            decay = max(0.0, 1 - idx * 0.1)
            insights.append(
                PrioritizedInsight(
                    title=title,
                    impact_score=cls._clamp(impact_score * decay),
                    urgency_score=cls._clamp(urgency_score * decay),
                    confidence=min(1.0, base_conf),
                )
            )

        # Highest impact first
        insights.sort(key=lambda i: (i.impact_score, i.urgency_score), reverse=True)
        return insights
