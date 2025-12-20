import apiClient from "../apiClient";
import {
  Anomaly,
  AnomaliesResponse,
  EngagementSummaryResponse,
  KpiSummaryResponse,
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
    const response = await apiClient.get<KpiSummaryResponse>("/insightops/analytics/kpis/summary", {
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
    const response = await apiClient.get<EngagementSummaryResponse>("/insightops/analytics/engagement/summary", {
      params: withDefaults({ org_id: orgId, signal_key: signalKey }),
    });
    return response.data;
  } catch (error) {
    handleError(error);
  }
}

export async function getAnomalies(
  { orgId = "demo_org", metricKey, signalKey }: AnomaliesParams = {}
): Promise<Anomaly[]> {
  try {
    const response = await apiClient.get<AnomaliesResponse>("/insightops/analytics/anomalies", {
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
