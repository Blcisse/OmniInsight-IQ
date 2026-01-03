"use client";
import { useEffect, useRef, useState } from "react";

export type LiveSummary = {
  window: string;
  since: string;
  total_revenue: number;
  orders_count: number;
  avg_order_value: number;
};

export function useLiveData(windowParam: "24h" | "7d" = "24h") {
  const [data, setData] = useState<LiveSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const load = async () => {
    try {
      setLoading(true);
      const res = await fetch(`/api/analytics/live?window=${windowParam}`);
      if (!res.ok) throw new Error(`Failed to fetch live: ${res.status}`);
      const json = (await res.json()) as LiveSummary;
      setData(json);
      setError(null);
    } catch (e: any) {
      setError(e?.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    timerRef.current && clearInterval(timerRef.current);
    timerRef.current = setInterval(load, 30000);
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [windowParam]);

  return { data, loading, error, refresh: load } as const;
}

