import { http, toApiResponse } from "./http";
import type { ApiResponse } from "./http";

export type CampaignQuery = {
  channel?: string;
  minROI?: number;
  limit?: number;
  offset?: number;
};

export type ConversionQuery = {
  startDate?: string;
  endDate?: string;
  limit?: number;
  offset?: number;
};

export async function getCampaignMetrics(filters: CampaignQuery = {}): Promise<ApiResponse<any>> {
  return toApiResponse(
    http.get("/api/marketing/campaign-metrics", {
      params: {
        channel: filters.channel,
        min_roi: filters.minROI,
        limit: filters.limit,
        offset: filters.offset,
      },
    })
  );
}

export async function getConversions(filters: ConversionQuery = {}): Promise<ApiResponse<any>> {
  return toApiResponse(
    http.get("/api/marketing/conversions", {
      params: {
        start_date: filters.startDate,
        end_date: filters.endDate,
        limit: filters.limit,
        offset: filters.offset,
      },
    })
  );
}
