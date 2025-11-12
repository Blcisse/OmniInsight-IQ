import { http, toApiResponse, ApiResponse } from "./http";

export async function getRecommendations(limit = 5): Promise<ApiResponse<any>> {
  return toApiResponse(http.get(`/api/insights/recommendations`, { params: { limit } }));
}
