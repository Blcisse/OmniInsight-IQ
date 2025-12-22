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

export type DriverAttribution = {
  primary_driver: string;
  supporting_factors?: string[];
  confidence?: number;
};

export type PrioritizedInsight = {
  title: string;
  impact_score: number;
  urgency_score: number;
  confidence: number;
  explainability_notes?: string[];
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
  driver_attribution?: DriverAttribution | null;
  prioritized_insights?: PrioritizedInsight[] | null;
  synthesis_block?: {
    situation: string;
    evidence: string;
    risk: string;
    opportunity: string;
    recommended_focus: string;
  } | null;
  executive_narrative?: {
    headline: string;
    why_now: string;
    top_drivers: string[];
    immediate_focus: string;
  } | null;
  top_drivers?: string[] | null;
  priority_focus?: string | null;
};
