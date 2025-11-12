import { http, toApiResponse, ApiResponse } from "./http";

export async function getAnalyticsSummary(): Promise<ApiResponse<any>> {
  return toApiResponse(http.get(`/api/analytics/`));
}

export async function getAnalyticsPredict(horizonDays = 5): Promise<ApiResponse<any>> {
  return toApiResponse(http.get(`/api/analytics/predict`, { params: { horizon_days: horizonDays } }));
}
