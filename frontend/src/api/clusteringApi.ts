import { http, toApiResponse, ApiResponse } from "./http";

export async function getCampaignClusters(k = 2): Promise<ApiResponse<any>> {
  return toApiResponse(http.get(`/api/model-inference/clusters`, { params: { entity: "campaign", k } }));
}
