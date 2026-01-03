import useSWR from "swr";
import { http } from "@/api/http";
import { mockAnalyticsAggregate, mockAnalyticsPredictions } from "@/store/utils/mockData";

async function fetcher<T>(url: string, params?: any): Promise<T> {
  const res = await http.get(url, { params });
  return res.data as T;
}

export function useAnalyticsAggregate() {
  const { data, error, isLoading, mutate } = useSWR(
    ["/api/analytics/"],
    ([url]) => fetcher(url).catch((e) => {
      if (e?.response?.status === 404) return mockAnalyticsAggregate;
      throw e;
    })
  );
  return { data, error, loading: isLoading, refresh: mutate } as const;
}

export function useAnalyticsForecast(horizonDays = 5) {
  const { data, error, isLoading, mutate } = useSWR(
    ["/api/analytics/predict", horizonDays],
    ([url, h]) => fetcher(url, { horizon_days: h }).catch((e) => {
      if (e?.response?.status === 404) return mockAnalyticsPredictions;
      throw e;
    })
  );
  return { data, error, loading: isLoading, refresh: mutate } as const;
}

