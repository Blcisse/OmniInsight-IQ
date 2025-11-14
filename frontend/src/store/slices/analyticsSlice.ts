import type { StateCreator } from "zustand";
import { getAnalyticsSummary, getAnalyticsPredict, getAnalyticsLive } from "@/api/analyticsApi";
import {
  mockAnalyticsAggregate,
  mockAnalyticsLive,
  mockAnalyticsPredictions,
} from "../utils/mockData";

/**
 * Analytics data types
 */
export type AnalyticsAggregate = {
  total_sales: number;
  avg_order_value: number;
  orders_count: number;
  revenue_growth_pct?: number;
  by_day: { date: string; sales: number }[];
};

export type AnalyticsPrediction = {
  forecast: number[];
  dates: string[];
  confidence: number;
};

export type AnalyticsState = {
  // Data
  aggregate: AnalyticsAggregate | null;
  predictions: AnalyticsPrediction | null;
  liveMetrics: Record<string, number | string> | null;

  // UI State
  loading: boolean;
  error: string | null;
  lastUpdated: number | null;

  // Filters
  dateRange: { start: string | null; end: string | null };
  selectedMetrics: string[];
};

export type AnalyticsActions = {
  // Data fetching
  fetchAggregate: () => Promise<void>;
  fetchPredictions: (horizonDays?: number) => Promise<void>;
  fetchLiveMetrics: (window?: string) => Promise<void>;
  refreshAnalytics: () => Promise<void>;

  // State updates
  setAggregate: (data: AnalyticsAggregate) => void;
  setPredictions: (data: AnalyticsPrediction) => void;
  setLiveMetrics: (data: Record<string, number | string>) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;

  // Filters
  setDateRange: (start: string | null, end: string | null) => void;
  setSelectedMetrics: (metrics: string[]) => void;
  resetFilters: () => void;
};

export type AnalyticsSlice = AnalyticsState & AnalyticsActions;

const initialState: AnalyticsState = {
  aggregate: null,
  predictions: null,
  liveMetrics: null,
  loading: false,
  error: null,
  lastUpdated: null,
  dateRange: { start: null, end: null },
  selectedMetrics: [],
};

export const createAnalyticsSlice: StateCreator<AnalyticsSlice> = (set, get) => ({
  ...initialState,

  fetchAggregate: async () => {
    set({ loading: true, error: null });
    try {
      const response = await getAnalyticsSummary();
      if (!response.ok) {
        throw Object.assign(new Error(response.error || "Failed to fetch analytics aggregate"), {
          status: response.status,
        });
      }
      set({
        aggregate: response.data,
        loading: false,
        lastUpdated: Date.now(),
      });
    } catch (error: any) {
      if (error?.status === 404) {
        set({
          aggregate: mockAnalyticsAggregate,
          loading: false,
          error: null,
          lastUpdated: Date.now(),
        });
        return;
      }
      set({
        error: error?.message || "Failed to fetch analytics",
        loading: false,
      });
    }
  },

  fetchPredictions: async (horizonDays = 5) => {
    set({ loading: true, error: null });
    try {
      const response = await getAnalyticsPredict(horizonDays);
      if (!response.ok) {
        throw Object.assign(new Error(response.error || "Failed to fetch predictions"), {
          status: response.status,
        });
      }
      const data = response.data;
      const today = new Date();
      const dates = Array.isArray(data?.forecast)
        ? data.forecast.map((_: number, idx: number) => {
            const d = new Date(today);
            d.setDate(d.getDate() + idx + 1);
            return d.toISOString().slice(0, 10);
          })
        : [];
      set({
        predictions: {
          forecast: data?.forecast ?? [],
          dates,
          confidence: data?.confidence ?? 0,
        },
        loading: false,
        lastUpdated: Date.now(),
      });
    } catch (error: any) {
      if (error?.status === 404) {
        set({
          predictions: mockAnalyticsPredictions,
          loading: false,
          error: null,
          lastUpdated: Date.now(),
        });
        return;
      }
      set({
        error: error?.message || "Failed to fetch predictions",
        loading: false,
      });
    }
  },

  fetchLiveMetrics: async (window = "24h") => {
    try {
      const response = await getAnalyticsLive(window);
      if (!response.ok) {
        throw Object.assign(new Error(response.error || "Failed to fetch live metrics"), {
          status: response.status,
        });
      }
      set({
        liveMetrics: response.data,
        lastUpdated: Date.now(),
        error: null,
      });
    } catch (error: any) {
      if (error?.status === 404) {
        set({
          liveMetrics: mockAnalyticsLive,
          lastUpdated: Date.now(),
          error: null,
        });
        return;
      }
      set({
        error: error?.message || "Failed to fetch live metrics",
      });
    }
  },

  refreshAnalytics: async () => {
    // Clear existing data to prevent duplication, then fetch fresh
    set({ loading: true, error: null });
    const { fetchAggregate, fetchPredictions, fetchLiveMetrics } = get();
    try {
      await Promise.all([fetchAggregate(), fetchPredictions(), fetchLiveMetrics()]);
    } catch (error: any) {
      set({
        error: error?.message || "Failed to refresh analytics",
        loading: false,
      });
    }
  },

  setAggregate: (data) => set({ aggregate: data, lastUpdated: Date.now() }),
  setPredictions: (data) => set({ predictions: data, lastUpdated: Date.now() }),
  setLiveMetrics: (data) => set({ liveMetrics: data, lastUpdated: Date.now() }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  setDateRange: (start, end) => set({ dateRange: { start, end } }),
  setSelectedMetrics: (metrics) => set({ selectedMetrics: metrics }),
  resetFilters: () =>
    set({
      dateRange: { start: null, end: null },
      selectedMetrics: [],
    }),
});
