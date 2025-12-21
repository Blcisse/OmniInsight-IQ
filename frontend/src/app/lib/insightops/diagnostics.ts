import { EngagementSummaryResponse, KpiSummaryResponse } from "./types";

export function isEmptyKpiSummary(summary: KpiSummaryResponse): boolean {
  const { latest_value, previous_value, absolute_delta, percent_delta, rolling_average_7d, rolling_average_7d_latest } =
    summary;
  return (
    (latest_value ?? null) === null &&
    (previous_value ?? null) === null &&
    (absolute_delta ?? null) === null &&
    (percent_delta ?? null) === null &&
    (rolling_average_7d ?? rolling_average_7d_latest ?? null) === null
  );
}

export function isEmptyEngagement(summary: EngagementSummaryResponse): boolean {
  const total = summary.total ?? summary.total_count ?? 0;
  return total === 0 && summary.average_per_day === 0 && summary.health_score === 0;
}

export function formatDelta(summary: KpiSummaryResponse): string {
  const delta = summary.percent_delta;
  if (delta === null || delta === undefined) {
    return "—";
  }
  const sign = delta > 0 ? "+" : "";
  return `${sign}${delta.toFixed(1)}%`;
}
