import { http, toApiResponse, ApiResponse } from "./http";

export interface ForecastPoint {
  date: string;
  value: number;
  lower_bound?: number;
  upper_bound?: number;
  confidence?: number;
}

export interface ForecastResponse {
  forecast: ForecastPoint[];
  history?: ForecastPoint[];
  confidence: number;
  model_type?: string;
}

/**
 * Get product forecast
 */
export async function getProductForecast(
  productId: string,
  opts?: { start?: string; end?: string }
): Promise<ApiResponse<any>> {
  const params: any = { product_id: productId };
  if (opts?.start) params.start = opts.start;
  if (opts?.end) params.end = opts.end;
  return toApiResponse(http.get(`/health-intel/products/metrics`, { params }));
}

/**
 * Get forecast from time series data
 */
export async function getForecast(
  history: Array<Record<string, any>>,
  dateCol: string = "date",
  targetCol: string = "value",
  horizon: number = 7
): Promise<ApiResponse<ForecastResponse>> {
  return toApiResponse(
    http.post("/analytics-dashboard/forecast/series", {
      history,
      date_col: dateCol,
      target_col: targetCol,
      forecast: horizon,
    })
  );
}

/**
 * Get model-based forecast
 */
export async function getModelForecast(
  modelName: string,
  features: Array<Record<string, any>>,
  horizon: number = 7
): Promise<ApiResponse<ForecastResponse>> {
  return toApiResponse(
    http.post("/api/model-inference/forecast", {
      model_name: modelName,
      features,
      horizon_days: horizon,
    })
  );
}
