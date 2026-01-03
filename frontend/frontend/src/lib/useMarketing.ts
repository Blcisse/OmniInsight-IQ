import useSWR from "swr";
import { http } from "@/api/http";
import { mockMarketingCampaigns, mockMarketingConversions } from "@/store/utils/mockData";

async function fetcher<T>(url: string, params?: any): Promise<T> {
  const res = await http.get(url, { params });
  return res.data as T;
}

export function useCampaigns(params?: { channel?: string; min_roi?: number; limit?: number; offset?: number }) {
  const { data, error, isLoading, mutate } = useSWR(
    ["/api/marketing/campaign-metrics", params],
    ([url, p]) => fetcher(url, p).catch((e) => {
      if (e?.response?.status === 404) return mockMarketingCampaigns as any;
      throw e;
    })
  );
  return { data: data || [], error, loading: isLoading, refresh: mutate } as const;
}

export function useConversions(params?: { start_date?: string; end_date?: string; limit?: number; offset?: number }) {
  const { data, error, isLoading, mutate } = useSWR(
    ["/api/marketing/conversions", params],
    ([url, p]) => fetcher(url, p).catch((e) => {
      if (e?.response?.status === 404) return mockMarketingConversions as any;
      throw e;
    })
  );
  return { data: data || [], error, loading: isLoading, refresh: mutate } as const;
}

