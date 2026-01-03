import type { StateCreator } from "zustand";

/**
 * Forecasting data types
 */
export type ForecastDataPoint = {
  date: string;
  value: number;
  lowerBound?: number;
  upperBound?: number;
  confidence?: number;
};

export type ProductForecast = {
  productId: string;
  productName?: string;
  forecast: ForecastDataPoint[];
  historical: ForecastDataPoint[];
  accuracy?: number;
  modelType?: string;
};

export type ForecastMetrics = {
  totalForecastedRevenue: number;
  forecastedGrowth: number;
  confidence: number;
  horizon: number;
  lastUpdated: string;
};

export type ForecastingState = {
  // Data
  forecasts: ProductForecast[];
  selectedForecast: ProductForecast | null;
  metrics: ForecastMetrics | null;

  // UI State
  loading: boolean;
  error: string | null;
  lastUpdated: number | null;

  // Configuration
  horizon: number; // days
  selectedProductIds: string[];
  dateRange: { start: string | null; end: string | null };
  modelType: string | null;
};

export type ForecastingActions = {
  // Data fetching
  fetchProductForecast: (productId: string, options?: { start?: string; end?: string }) => Promise<void>;
  fetchMultipleForecasts: (productIds: string[]) => Promise<void>;
  fetchForecastMetrics: () => Promise<void>;
  refreshForecasting: () => Promise<void>;

  // State updates
  setForecasts: (forecasts: ProductForecast[]) => void;
  setSelectedForecast: (forecast: ProductForecast | null) => void;
  setMetrics: (metrics: ForecastMetrics) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;

  // Configuration
  setHorizon: (days: number) => void;
  setSelectedProductIds: (ids: string[]) => void;
  setDateRange: (start: string | null, end: string | null) => void;
  setModelType: (type: string | null) => void;
  resetConfiguration: () => void;
};

export type ForecastingSlice = ForecastingState & ForecastingActions;

const initialState: ForecastingState = {
  forecasts: [],
  selectedForecast: null,
  metrics: null,
  loading: false,
  error: null,
  lastUpdated: null,
  horizon: 30,
  selectedProductIds: [],
  dateRange: { start: null, end: null },
  modelType: null,
};

export const createForecastingSlice: StateCreator<ForecastingSlice> = (set, get) => ({
  ...initialState,

  fetchProductForecast: async (productId, options = {}) => {
    set({ loading: true, error: null });
    try {
      const params = new URLSearchParams({ product_id: productId });
      if (options.start) params.append("start", options.start);
      if (options.end) params.append("end", options.end);

      const response = await fetch(`/health-intel/products/metrics?${params.toString()}`);
      if (!response.ok) throw new Error("Failed to fetch product forecast");
      const data = await response.json();
      
      const { forecasts } = get();
      const existingIndex = forecasts.findIndex((f) => f.productId === productId);
      const updatedForecast: ProductForecast = {
        productId,
        ...data,
      };

      set({
        forecasts:
          existingIndex >= 0
            ? forecasts.map((f, i) => (i === existingIndex ? updatedForecast : f))
            : [...forecasts, updatedForecast],
        loading: false,
        lastUpdated: Date.now(),
      });
    } catch (error: any) {
      set({
        error: error?.message || "Failed to fetch product forecast",
        loading: false,
      });
    }
  },

  fetchMultipleForecasts: async (productIds: string[]) => {
    set({ loading: true, error: null });
    try {
      const { horizon, dateRange } = get();
      const promises = productIds.map((id) =>
        get().fetchProductForecast(id, {
          start: dateRange.start || undefined,
          end: dateRange.end || undefined,
        })
      );
      await Promise.all(promises);
      set({ loading: false });
    } catch (error: any) {
      set({
        error: error?.message || "Failed to fetch forecasts",
        loading: false,
      });
    }
  },

  fetchForecastMetrics: async () => {
    set({ loading: true, error: null });
    try {
      const { horizon } = get();
      const response = await fetch(`/api/forecasting/metrics?horizon=${horizon}`);
      if (!response.ok) throw new Error("Failed to fetch forecast metrics");
      const data = await response.json();
      set({
        metrics: data,
        loading: false,
        lastUpdated: Date.now(),
      });
    } catch (error: any) {
      set({
        error: error?.message || "Failed to fetch forecast metrics",
        loading: false,
      });
    }
  },

  refreshForecasting: async () => {
    // Clear existing forecasts to prevent duplication, then fetch fresh
    set({ loading: true, error: null, forecasts: [] });
    const { fetchMultipleForecasts, fetchForecastMetrics, selectedProductIds } = get();
    try {
      if (selectedProductIds.length > 0) {
        await fetchMultipleForecasts(selectedProductIds);
      }
      await fetchForecastMetrics();
    } catch (error: any) {
      set({
        error: error?.message || "Failed to refresh forecasting data",
        loading: false,
      });
    }
  },

  setForecasts: (forecasts) => set({ forecasts, lastUpdated: Date.now() }),
  setSelectedForecast: (forecast) => set({ selectedForecast: forecast }),
  setMetrics: (metrics) => set({ metrics, lastUpdated: Date.now() }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  setHorizon: (days) => set({ horizon: days }),
  setSelectedProductIds: (ids) => set({ selectedProductIds: ids }),
  setDateRange: (start, end) => set({ dateRange: { start, end } }),
  setModelType: (type) => set({ modelType: type }),
  resetConfiguration: () =>
    set({
      horizon: 30,
      selectedProductIds: [],
      dateRange: { start: null, end: null },
      modelType: null,
    }),
});
