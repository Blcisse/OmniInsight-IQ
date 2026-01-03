"use client";
import { useCallback, useEffect, useRef, useState } from "react";

type FetchState<T> = {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
};

const cache = new Map<string, any>();

export function useFetchData<T = unknown>(url: string, opts?: RequestInit): FetchState<T> {
  const [data, setData] = useState<T | null>(() => (cache.has(url) ? cache.get(url) : null));
  const [loading, setLoading] = useState<boolean>(!cache.has(url));
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const load = useCallback(async () => {
    if (!url) return;
    setLoading(true);
    setError(null);

    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const res = await fetch(url, { ...(opts || {}), method: "GET", signal: controller.signal });
      if (!res.ok) throw new Error(`Request failed: ${res.status}`);
      const json = (await res.json()) as T;
      cache.set(url, json);
      setData(json);
    } catch (e: any) {
      if (e?.name === "AbortError") return;
      setError(e?.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  }, [url, opts]);

  useEffect(() => {
    if (!cache.has(url)) {
      load();
    }
    return () => abortRef.current?.abort();
  }, [url, load]);

  return { data, loading, error, refetch: load } as FetchState<T>;
}

