import { http, toApiResponse, ApiResponse } from "./http";

export interface AnomalyData {
  date: string;
  value: number;
  score?: number;
  is_anomaly: boolean;
}

export interface AnomalySeriesResponse {
  series: Array<{ date: string; value: number }>;
  anomalies: Array<{ date: string; value: number; score: number }>;
}

export interface AnomalySummaryResponse {
  series: Array<{ date: string; count: number; score: number }>;
}

/**
 * Get anomalies from time series data
 */
export async function getAnomalies(
  history: Array<Record<string, any>>,
  dateCol: string = "date",
  valueCol: string = "value",
  method: string = "zscore",
  threshold: number = 3.0
): Promise<ApiResponse<AnomalySeriesResponse>> {
  return toApiResponse(
    http.post("/analytics-dashboard/anomaly/series", {
      history,
      date_col: dateCol,
      value_col: valueCol,
      method,
      threshold,
    })
  );
}

/**
 * Get anomaly summary
 */
export async function getAnomalySummary(
  anomalies: Array<Record<string, any>>,
  dateCol: string = "date",
  scoreCol?: string
): Promise<ApiResponse<AnomalySummaryResponse>> {
  return toApiResponse(
    http.post("/analytics-dashboard/anomaly/summary", {
      anomalies,
      date_col: dateCol,
      score_col: scoreCol,
    })
  );
}

/**
 * Detect anomalies in sales data
 */
export async function detectSalesAnomalies(threshold: number = 2.0): Promise<ApiResponse<AnomalyData[]>> {
  return toApiResponse(http.get("/api/analytics/anomalies", { params: { threshold } }));
}

