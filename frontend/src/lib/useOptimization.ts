import useSWR from "swr";
import { http } from "@/api/http";
import { mockOptimizationMetrics, mockOptimizationRecommendations } from "@/store/utils/mockData";

async function fetcher<T>(url: string): Promise<T> {
  const res = await http.get(url);
  return res.data as T;
}

export function useOptimizationMetrics() {
  const { data, error, isLoading, mutate } = useSWR(
    ["/api/optimization/metrics"],
    ([url]) => fetcher(url).catch((e) => {
      if (e?.response?.status === 404) return mockOptimizationMetrics as any;
      throw e;
    })
  );
  return { data, error, loading: isLoading, refresh: mutate } as const;
}

export function useOptimizationRecommendations() {
  const { data, error, isLoading, mutate } = useSWR(
    ["/api/optimization/recommendations"],
    ([url]) => fetcher(url).catch((e) => {
      if (e?.response?.status === 404) return mockOptimizationRecommendations as any;
      throw e;
    })
  );
  return { data: data || [], error, loading: isLoading, refresh: mutate } as const;
}

