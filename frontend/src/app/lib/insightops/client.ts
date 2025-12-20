// InsightOps frontend uses Next.js API proxy routes under /api/insightops/* to avoid CORS and keep backend base URL configurable.
import apiClient from "../apiClient";
import {
  Anomaly,
  AnomaliesResponse,
  EngagementSummaryResponse,
  KpiSummaryResponse,
  SeriesPoint,
} from "./types";

type KpiSummaryParams = {
  orgId?: string;
  metricKey?: string;
};

type EngagementSummaryParams = {
  orgId?: string;
  signalKey?: string;
};

type AnomaliesParams = {
  orgId?: string;
  metricKey?: string;
  signalKey?: string;
};

type KpiSeriesParams = {
  orgId?: string;
  metricKey?: string;
  lookbackDays?: number;
};

type EngagementSeriesParams = {
  orgId?: string;
  signalKey?: string;
  lookbackDays?: number;
};

const withDefaults = <T extends Record<string, unknown>>(params: T) => ({
  orgId: "demo_org",
  ...params,
});

const handleError = (error: any) => {
  const status = error?.response?.status;
  const message = error?.response?.data?.detail || error.message || "Request failed";
  throw new Error(`InsightOps API error (${status ?? "unknown"}): ${message}`);
};

export async function getKpiSummary(
  { orgId = "demo_org", metricKey = "revenue" }: KpiSummaryParams = {}
): Promise<KpiSummaryResponse> {
  try {
    const response = await apiClient.get<KpiSummaryResponse>("/api/insightops/analytics/kpis/summary", {
      params: withDefaults({ org_id: orgId, metric_key: metricKey }),
    });
    return response.data;
  } catch (error) {
    handleError(error);
  }
}

export async function getEngagementSummary(
  { orgId = "demo_org", signalKey = "touches" }: EngagementSummaryParams = {}
): Promise<EngagementSummaryResponse> {
  try {
    const response = await apiClient.get<EngagementSummaryResponse>("/api/insightops/analytics/engagement/summary", {
      params: withDefaults({ org_id: orgId, signal_key: signalKey }),
    });
    return response.data;
  } catch (error) {
    handleError(error);
  }
}

const normalizeSeries = (data: any): SeriesPoint[] => {
  if (Array.isArray(data)) {
    return data as SeriesPoint[];
  }
  if (data?.points && Array.isArray(data.points)) {
    return data.points as SeriesPoint[];
  }
  return [];
};

export async function getKpiSeries(
  { orgId = "demo_org", metricKey = "revenue", lookbackDays = 14 }: KpiSeriesParams = {}
): Promise<SeriesPoint[]> {
  try {
    const response = await apiClient.get("/api/insightops/analytics/kpis/series", {
      params: withDefaults({
        org_id: orgId,
        metric_key: metricKey,
        lookback_days: lookbackDays,
      }),
    });
    return normalizeSeries(response.data);
  } catch (error) {
    handleError(error);
  }
}

export async function getEngagementSeries(
  { orgId = "demo_org", signalKey = "touches", lookbackDays = 14 }: EngagementSeriesParams = {}
): Promise<SeriesPoint[]> {
  try {
    const response = await apiClient.get("/api/insightops/analytics/engagement/series", {
      params: withDefaults({
        org_id: orgId,
        signal_key: signalKey,
        lookback_days: lookbackDays,
      }),
    });
    return normalizeSeries(response.data);
  } catch (error) {
    handleError(error);
  }
}

export async function getAnomalies(
  { orgId = "demo_org", metricKey, signalKey }: AnomaliesParams = {}
): Promise<Anomaly[]> {
  try {
    const response = await apiClient.get<AnomaliesResponse>("/api/insightops/analytics/anomalies", {
      params: withDefaults({ org_id: orgId, metric_key: metricKey, signal_key: signalKey }),
    });
    const payload = response.data;
    if (Array.isArray(payload)) {
      return payload;
    }
    if (payload && Array.isArray((payload as any).anomalies)) {
      return (payload as any).anomalies;
    }
    return [];
  } catch (error) {
    handleError(error);
  }
}
