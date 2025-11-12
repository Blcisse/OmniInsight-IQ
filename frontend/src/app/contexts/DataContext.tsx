"use client";
import React, { createContext, useContext, useEffect, useMemo, useState } from "react";

type DataState = {
  sales: any[];
  marketing: any;
  analytics: any;
  loading: boolean;
  error?: string;
};

type DataContextValue = DataState & {
  refresh: () => Promise<void>;
};

const DataContext = createContext<DataContextValue | undefined>(undefined);

async function fetchJSON(path: string) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`Failed to fetch ${path}`);
  return res.json();
}

export function DataProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<DataState>({ sales: [], marketing: null, analytics: null, loading: true });

  const load = async () => {
    try {
      setState((s) => ({ ...s, loading: true, error: undefined }));
      // These paths assume the Next.js app will proxy or serve static mocks.
      const [sales, marketing, analytics] = await Promise.all([
        fetchJSON("/api/sales"),
        fetchJSON("/api/marketing/campaign-metrics"),
        fetchJSON("/api/analytics"),
      ]);
      setState({ sales, marketing: { campaigns: marketing }, analytics, loading: false });
    } catch (e: any) {
      setState((s) => ({ ...s, loading: false, error: e?.message || "Load failed" }));
    }
  };

  useEffect(() => {
    load();
  }, []);

  const value = useMemo(() => ({ ...state, refresh: load }), [state]);

  return <DataContext.Provider value={value}>{children}</DataContext.Provider>;
}

export function useData() {
  const ctx = useContext(DataContext);
  if (!ctx) throw new Error("useData must be used within DataProvider");
  return ctx;
}

