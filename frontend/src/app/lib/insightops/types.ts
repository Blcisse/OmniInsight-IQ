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

export type ExecutiveInsight = {
  title: string;
  summary: string;
  severity: number;
  category: string;
};

export type ExecutiveRisk = {
  title: string;
  description: string;
  severity: number;
  mitigation?: string | null;
};

export type ExecutiveOpportunity = {
  title: string;
  description: string;
  confidence: number;
};

export type ExecutiveBriefResponse = {
  org_id: string;
  generated_at: string;
  window_days: number;
  priority_score: number;
  priority_level: string;
  insights: ExecutiveInsight[];
  risks: ExecutiveRisk[];
  opportunities: ExecutiveOpportunity[];
  notes: string[];
  saved?: boolean;
  summary_id?: string | null;
  summary_type?: string | null;
};
