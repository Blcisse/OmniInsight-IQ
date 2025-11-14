import { createStore } from "zustand";
import { useStore } from "zustand";

import type { AnalyticsSlice } from "./slices/analyticsSlice";
import { createAnalyticsSlice } from "./slices/analyticsSlice";
import type { MarketingSlice } from "./slices/marketingSlice";
import { createMarketingSlice } from "./slices/marketingSlice";
import type { OptimizationSlice } from "./slices/optimizationSlice";
import { createOptimizationSlice } from "./slices/optimizationSlice";
import type { ForecastingSlice } from "./slices/forecastingSlice";
import { createForecastingSlice } from "./slices/forecastingSlice";
import type { NutritionIntelligenceSlice } from "./slices/nutritionIntelligenceSlice";
import { createNutritionIntelligenceSlice } from "./slices/nutritionIntelligenceSlice";

export type SliceName =
  | "analytics"
  | "marketing"
  | "optimization"
  | "forecasting"
  | "nutritionIntelligence";

export type KPIData = {
  label: string;
  value: number | string;
  delta?: number;
  metadata?: Record<string, unknown>;
};

export type CommonActions = {
  setData: <T = unknown>(sliceName: SliceName, payload: T) => void;
  updateKPI: (sliceName: SliceName, kpiData: KPIData | KPIData[]) => void;
};

export type DashboardStore = AnalyticsSlice &
  MarketingSlice &
  OptimizationSlice &
  ForecastingSlice &
  NutritionIntelligenceSlice &
  CommonActions;

const createDashboardStore = () =>
  createStore<DashboardStore>((set, get) => ({
    ...createAnalyticsSlice(set, get, undefined),
    ...createMarketingSlice(set, get, undefined),
    ...createOptimizationSlice(set, get, undefined),
    ...createForecastingSlice(set, get, undefined),
    ...createNutritionIntelligenceSlice(set, get, undefined),

    setData: <T = unknown>(sliceName: SliceName, payload: T) => {
      const state = get();
      switch (sliceName) {
        case "analytics":
          if (typeof payload === "object" && payload !== null) {
            if ("aggregate" in payload) state.setAggregate((payload as any).aggregate);
            if ("predictions" in payload) state.setPredictions((payload as any).predictions);
            if ("liveMetrics" in payload) state.setLiveMetrics((payload as any).liveMetrics);
          }
          break;
        case "marketing":
          if (typeof payload === "object" && payload !== null) {
            if ("campaigns" in payload) state.setCampaigns((payload as any).campaigns);
            if ("conversions" in payload) state.setConversions((payload as any).conversions);
          }
          break;
        case "optimization":
          if (typeof payload === "object" && payload !== null) {
            if ("recommendations" in payload) state.setRecommendations((payload as any).recommendations);
            if ("metrics" in payload) state.setMetrics((payload as any).metrics);
          }
          break;
        case "forecasting":
          if (typeof payload === "object" && payload !== null) {
            if ("forecasts" in payload) state.setForecasts((payload as any).forecasts);
            if ("metrics" in payload) state.setMetrics((payload as any).metrics);
          }
          break;
        case "nutritionIntelligence":
          if (typeof payload === "object" && payload !== null) {
            if ("insights" in payload) state.setInsights((payload as any).insights);
            if ("productData" in payload) state.setProductData((payload as any).productData);
            if ("trends" in payload) state.setTrends((payload as any).trends);
          }
          break;
      }
    },

    updateKPI: (sliceName: SliceName, kpiData: KPIData | KPIData[]) => {
      const state = get();
      const kpis = Array.isArray(kpiData) ? kpiData : [kpiData];
      switch (sliceName) {
        case "analytics":
          if (state.aggregate) {
            const updates: Partial<typeof state.aggregate> = {};
            kpis.forEach((kpi) => {
              if (kpi.label.toLowerCase().includes("sales") && typeof kpi.value === "number") {
                updates.total_sales = kpi.value;
              }
              if (kpi.label.toLowerCase().includes("order") && typeof kpi.value === "number") {
                if (kpi.label.toLowerCase().includes("avg")) updates.avg_order_value = kpi.value;
                else updates.orders_count = kpi.value;
              }
            });
            state.setAggregate({ ...state.aggregate, ...updates });
          }
          break;
        case "optimization":
          if (state.metrics) {
            const updates: Partial<typeof state.metrics> = {};
            kpis.forEach((kpi) => {
              if (kpi.label.toLowerCase().includes("efficiency") && typeof kpi.value === "number") {
                if (kpi.label.toLowerCase().includes("current")) updates.currentEfficiency = kpi.value;
                else if (kpi.label.toLowerCase().includes("target")) updates.targetEfficiency = kpi.value;
              }
            });
            state.setMetrics({ ...state.metrics, ...updates });
          }
          break;
        case "forecasting":
          if (state.metrics) {
            const updates: Partial<typeof state.metrics> = {};
            kpis.forEach((kpi) => {
              if (kpi.label.toLowerCase().includes("revenue") && typeof kpi.value === "number") {
                updates.totalForecastedRevenue = kpi.value;
              }
              if (kpi.label.toLowerCase().includes("growth") && typeof kpi.value === "number") {
                updates.forecastedGrowth = kpi.value;
              }
            });
            state.setMetrics({ ...state.metrics, ...updates });
          }
          break;
      }
    },

  }));

const dashboardStoreInternal = createDashboardStore();

export const useDashboardStore = <T,>(selector: (state: DashboardStore) => T, equalityFn?: (a: T, b: T) => boolean) =>
  useStore(dashboardStoreInternal, selector, equalityFn);

export const dashboardStore = dashboardStoreInternal;
