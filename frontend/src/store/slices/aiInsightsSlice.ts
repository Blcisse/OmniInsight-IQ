import type { StateCreator } from "zustand";
import type { Cluster } from "@/api/clusteringApi";
import type { AnomalyData } from "@/api/anomalyApi";
import type { ForecastResponse } from "@/api/forecastingApi";
import type { RecommendationResponse } from "@/api/recommendationsApi";

/**
 * AI Insights data types
 */
export type AIInsightsState = {
  // Clustering
  clusters: Cluster[];
  clusterDistribution: Array<{ cluster: number; count: number }> | null;
  selectedCluster: number | null;

  // Anomaly Detection
  anomalies: AnomalyData[];
  anomalySummary: Array<{ date: string; count: number; score: number }> | null;

  // Forecasting
  forecasts: ForecastResponse[];
  selectedForecast: ForecastResponse | null;

  // Recommendations
  recommendations: RecommendationResponse | null;

  // UI State (using unique names to avoid conflicts)
  aiLoading: boolean;
  aiError: string | null;
  lastUpdated: number | null;

  // Dataset selection
  currentDataset: string | null;
  availableDatasets: string[];
  
  // Note: These properties might conflict with other slices, so we'll use unique names
  aiLoading: boolean;
  aiError: string | null;
};

export type AIInsightsActions = {
  // Clustering
  fetchClusters: (entity?: string, k?: number) => Promise<void>;
  fetchClusterDistribution: (data: Array<Record<string, any>>, clusterCol?: string) => Promise<void>;
  fetchClusterInsights: (data: Array<Record<string, any>>, clusterCol?: string, featureCols?: string[]) => Promise<void>;
  setSelectedCluster: (cluster: number | null) => void;

  // Anomaly Detection
  fetchAnomalies: (history: Array<Record<string, any>>, dateCol?: string, valueCol?: string) => Promise<void>;
  fetchAnomalySummary: (anomalies: Array<Record<string, any>>, dateCol?: string) => Promise<void>;
  detectSalesAnomalies: (threshold?: number) => Promise<void>;

  // Forecasting
  fetchForecast: (history: Array<Record<string, any>>, dateCol?: string, targetCol?: string, horizon?: number) => Promise<void>;
  fetchModelForecast: (modelName: string, features: Array<Record<string, any>>, horizon?: number) => Promise<void>;
  setSelectedForecast: (forecast: ForecastResponse | null) => void;

  // Recommendations
  fetchRecommendations: (limit?: number) => Promise<void>;
  fetchModelRecommendations: (userId?: string, itemIds?: string[], topK?: number) => Promise<void>;

  // Dataset management
  setCurrentDataset: (dataset: string) => Promise<void>;
  refreshAIInsights: () => Promise<void>;

  // State updates
  setClusters: (clusters: Cluster[]) => void;
  setAnomalies: (anomalies: AnomalyData[]) => void;
  setForecasts: (forecasts: ForecastResponse[]) => void;
  setRecommendations: (recommendations: RecommendationResponse) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
};

export type AIInsightsSlice = AIInsightsState & AIInsightsActions;

const initialState: AIInsightsState = {
  clusters: [],
  clusterDistribution: null,
  selectedCluster: null,
  anomalies: [],
  anomalySummary: null,
  forecasts: [],
  selectedForecast: null,
  recommendations: null,
  aiLoading: false,
  aiError: null,
  lastUpdated: null,
  currentDataset: null,
  availableDatasets: [],
};

export const createAIInsightsSlice: StateCreator<AIInsightsSlice> = (set, get) => ({
  ...initialState,

  fetchClusters: async (entity = "campaign", k = 2) => {
    set({ aiLoading: true, aiError: null });
    try {
      const { getClusters } = await import("@/api/clusteringApi");
      const response = await getClusters(entity, k);
      if (!response.ok) throw new Error(response.error || "Failed to fetch clusters");
      set({
        clusters: response.data || [],
        aiLoading: false,
        lastUpdated: Date.now(),
      });
    } catch (error: any) {
      set({
        aiError: error?.message || "Failed to fetch clusters",
        aiLoading: false,
      });
    }
  },

  fetchClusterDistribution: async (data, clusterCol = "cluster") => {
    set({ aiLoading: true, aiError: null });
    try {
      const { getClusterDistribution } = await import("@/api/clusteringApi");
      const response = await getClusterDistribution(data, clusterCol);
      if (!response.ok) throw new Error(response.error || "Failed to fetch cluster distribution");
      set({
        clusterDistribution: response.data?.clusters || null,
        aiLoading: false,
        lastUpdated: Date.now(),
      });
    } catch (error: any) {
      set({
        aiError: error?.message || "Failed to fetch cluster distribution",
        aiLoading: false,
      });
    }
  },

  fetchClusterInsights: async (data, clusterCol = "cluster", featureCols) => {
    set({ aiLoading: true, aiError: null });
    try {
      const { getClusterInsights } = await import("@/api/clusteringApi");
      const response = await getClusterInsights(data, clusterCol, featureCols);
      if (!response.ok) throw new Error(response.error || "Failed to fetch cluster insights");
      // Store insights in clusters if needed
      set({
        aiLoading: false,
        lastUpdated: Date.now(),
      });
    } catch (error: any) {
      set({
        aiError: error?.message || "Failed to fetch cluster insights",
        aiLoading: false,
      });
    }
  },

  setSelectedCluster: (cluster) => set({ selectedCluster: cluster }),

  fetchAnomalies: async (history, dateCol = "date", valueCol = "value") => {
    set({ aiLoading: true, aiError: null });
    try {
      const { getAnomalies } = await import("@/api/anomalyApi");
      const response = await getAnomalies(history, dateCol, valueCol);
      if (!response.ok) throw new Error(response.error || "Failed to fetch anomalies");
      const anomalies: AnomalyData[] = (response.data?.anomalies || []).map((a: any) => ({
        date: a.date,
        value: a.value,
        score: a.score,
        is_anomaly: true,
      }));
      set({
        anomalies,
        aiLoading: false,
        lastUpdated: Date.now(),
      });
    } catch (error: any) {
      set({
        aiError: error?.message || "Failed to fetch anomalies",
        aiLoading: false,
      });
    }
  },

  fetchAnomalySummary: async (anomalies, dateCol = "date") => {
    set({ aiLoading: true, aiError: null });
    try {
      const { getAnomalySummary } = await import("@/api/anomalyApi");
      const response = await getAnomalySummary(anomalies, dateCol);
      if (!response.ok) throw new Error(response.error || "Failed to fetch anomaly summary");
      set({
        anomalySummary: response.data?.series || null,
        aiLoading: false,
        lastUpdated: Date.now(),
      });
    } catch (error: any) {
      set({
        aiError: error?.message || "Failed to fetch anomaly summary",
        aiLoading: false,
      });
    }
  },

  detectSalesAnomalies: async (threshold = 2.0) => {
    set({ aiLoading: true, aiError: null });
    try {
      const { detectSalesAnomalies } = await import("@/api/anomalyApi");
      const response = await detectSalesAnomalies(threshold);
      if (!response.ok) throw new Error(response.error || "Failed to detect anomalies");
      set({
        anomalies: response.data || [],
        aiLoading: false,
        lastUpdated: Date.now(),
      });
    } catch (error: any) {
      set({
        aiError: error?.message || "Failed to detect anomalies",
        aiLoading: false,
      });
    }
  },

  fetchForecast: async (history, dateCol = "date", targetCol = "value", horizon = 7) => {
    set({ aiLoading: true, aiError: null });
    try {
      const { getForecast } = await import("@/api/forecastingApi");
      const response = await getForecast(history, dateCol, targetCol, horizon);
      if (!response.ok) throw new Error(response.error || "Failed to fetch forecast");
      const forecast: ForecastResponse = response.data || { forecast: [], confidence: 0 };
      const { forecasts } = get();
      set({
        forecasts: [...forecasts, forecast],
        selectedForecast: forecast,
        aiLoading: false,
        lastUpdated: Date.now(),
      });
    } catch (error: any) {
      set({
        aiError: error?.message || "Failed to fetch forecast",
        aiLoading: false,
      });
    }
  },

  fetchModelForecast: async (modelName, features, horizon = 7) => {
    set({ aiLoading: true, aiError: null });
    try {
      const { getModelForecast } = await import("@/api/forecastingApi");
      const response = await getModelForecast(modelName, features, horizon);
      if (!response.ok) throw new Error(response.error || "Failed to fetch model forecast");
      const forecast: ForecastResponse = response.data || { forecast: [], confidence: 0 };
      set({
        forecasts: [...get().forecasts, forecast],
        selectedForecast: forecast,
        aiLoading: false,
        lastUpdated: Date.now(),
      });
    } catch (error: any) {
      set({
        aiError: error?.message || "Failed to fetch model forecast",
        aiLoading: false,
      });
    }
  },

  setSelectedForecast: (forecast) => set({ selectedForecast: forecast }),

  fetchRecommendations: async (limit = 5) => {
    set({ aiLoading: true, aiError: null });
    try {
      const { getRecommendations } = await import("@/api/recommendationsApi");
      const response = await getRecommendations(limit);
      if (!response.ok) throw new Error(response.error || "Failed to fetch recommendations");
      set({
        recommendations: response.data || null,
        aiLoading: false,
        lastUpdated: Date.now(),
      });
    } catch (error: any) {
      set({
        aiError: error?.message || "Failed to fetch recommendations",
        aiLoading: false,
      });
    }
  },

  fetchModelRecommendations: async (userId, itemIds, topK = 10) => {
    set({ aiLoading: true, aiError: null });
    try {
      const { getModelRecommendations } = await import("@/api/recommendationsApi");
      const response = await getModelRecommendations(userId, itemIds, undefined, topK);
      if (!response.ok) throw new Error(response.error || "Failed to fetch model recommendations");
      set({
        recommendations: response.data || null,
        aiLoading: false,
        lastUpdated: Date.now(),
      });
    } catch (error: any) {
      set({
        aiError: error?.message || "Failed to fetch model recommendations",
        aiLoading: false,
      });
    }
  },

  setCurrentDataset: async (dataset) => {
    set({ currentDataset: dataset, aiLoading: true });
    // When dataset changes, trigger all AI computations
    const { refreshAIInsights } = get();
    await refreshAIInsights();
  },

  refreshAIInsights: async () => {
    // Clear existing data to prevent duplication, then fetch fresh
    set({ aiLoading: true, aiError: null, clusters: [], anomalies: [], forecasts: [], recommendations: null });
    const { fetchClusters, detectSalesAnomalies, fetchRecommendations } = get();
    try {
      await Promise.all([
        fetchClusters("campaign", 3),
        detectSalesAnomalies(2.0),
        fetchRecommendations(5),
      ]);
    } catch (error: any) {
      set({
        aiError: error?.message || "Failed to refresh AI insights",
        aiLoading: false,
      });
    }
  },

  setClusters: (clusters) => set({ clusters, lastUpdated: Date.now() }),
  setAnomalies: (anomalies) => set({ anomalies, lastUpdated: Date.now() }),
  setForecasts: (forecasts) => set({ forecasts, lastUpdated: Date.now() }),
  setRecommendations: (recommendations) => set({ recommendations, lastUpdated: Date.now() }),
  setLoading: (loading) => set({ aiLoading: loading }),
  setError: (error) => set({ aiError: error }),
});

