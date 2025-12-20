export type SeriesPoint = {
  date: string;
  value: number | null;
};

export type KpiSummaryResponse = {
  latest_value: number | null;
  previous_value: number | null;
  absolute_delta: number | null;
  percent_delta: number | null;
  rolling_average_7d?: number | null;
  rolling_average_7d_latest?: number | null;
};

export type EngagementSummaryResponse = {
  total_count?: number;
  total?: number;
  average_per_day: number;
  last_day_value: number | null;
  health_score: number;
};

export type Anomaly = {
  type: string;
  severity: "info" | "warning" | "critical";
  description: string;
  date: string;
};

export type AnomaliesResponse =
  | Anomaly[]
  | {
      anomalies: Anomaly[];
    };
