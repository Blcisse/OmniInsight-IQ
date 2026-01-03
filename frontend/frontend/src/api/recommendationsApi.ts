import { http, toApiResponse, ApiResponse } from "./http";

export interface Recommendation {
  item: string;
  score: number;
  reason?: string;
  category?: string;
}

export interface RecommendationResponse {
  recommendations: Recommendation[];
  user_id?: string;
  context?: Record<string, any>;
}

export interface RecommendationTrends {
  trends: Array<{
    date: string;
    item: string;
    score: number;
  }>;
}

/**
 * Get recommendations
 */
export async function getRecommendations(limit = 5): Promise<ApiResponse<RecommendationResponse>> {
  return toApiResponse(http.get(`/api/insights/recommendations`, { params: { limit } }));
}

/**
 * Get model-based recommendations
 */
export async function getModelRecommendations(
  userId?: string,
  itemIds?: string[],
  userRatings?: Record<string, number>,
  topK: number = 10
): Promise<ApiResponse<RecommendationResponse>> {
  return toApiResponse(
    http.post("/api/model-inference/recommend", {
      user_id: userId,
      item_ids: itemIds,
      user_ratings: userRatings,
      top_k: topK,
    })
  );
}

/**
 * Get recommendation item scores
 */
export async function getRecommendationScores(
  items: string[],
  context?: Record<string, any>
): Promise<ApiResponse<Array<{ item: string; score: number }>>> {
  return toApiResponse(
    http.post("/analytics-dashboard/recommendation/item-scores", {
      items,
      context,
    })
  );
}

/**
 * Get recommendation trends
 */
export async function getRecommendationTrends(
  items: string[],
  dateCol: string = "date",
  startDate?: string,
  endDate?: string
): Promise<ApiResponse<RecommendationTrends>> {
  return toApiResponse(
    http.post("/analytics-dashboard/recommendation/trends", {
      items,
      date_col: dateCol,
      start_date: startDate,
      end_date: endDate,
    })
  );
}
