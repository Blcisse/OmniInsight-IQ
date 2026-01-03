import { http, toApiResponse, ApiResponse } from "./http";

export interface FoodItem {
  food_name: string;
  calories?: number;
  fat?: number;
  protein?: number;
  carbohydrates?: number;
  sugars?: number;
  dietary_fiber?: number;
  data_group?: string;
}

export interface FoodAnalyticsSummary {
  total_foods: number;
  avg_calories: number;
  avg_protein: number;
  avg_fat: number;
  avg_carbs: number;
  categories: Record<string, number>;
}

export interface FoodStats {
  total_items: number;
  nutrition_stats: {
    calories: { min: number; max: number; avg: number };
    protein: { min: number; max: number; avg: number };
    fat: { min: number; max: number; avg: number };
  };
  by_group: Record<string, number>;
}

/**
 * Get processed food data
 */
export async function getFoodData(
  group?: string,
  limit = 100,
  offset = 0
): Promise<ApiResponse<FoodItem[]>> {
  const params: any = { limit, offset };
  if (group) params.group = group;
  return toApiResponse(http.get("/api/processed-data/food", { params }));
}

/**
 * Get food analytics summary
 */
export async function getFoodAnalyticsSummary(): Promise<ApiResponse<FoodAnalyticsSummary>> {
  return toApiResponse(http.get("/api/processed-data/food/summary"));
}

/**
 * Get food statistics for KPIs
 */
export async function getFoodStats(): Promise<ApiResponse<FoodStats>> {
  return toApiResponse(http.get("/api/processed-data/food/stats"));
}

