import { useDashboardStore, dashboardStore } from "./dashboardStore";
import { shallow } from "zustand/shallow";

/* ---------------------------
   Reactive hooks for each slice
--------------------------- */

/** Analytics Slice */
export function useAnalyticsStore() {
  return useDashboardStore(
    (state) => ({
      aggregate: state.aggregate,
      predictions: state.predictions,
      liveMetrics: state.liveMetrics,
      loading: state.loading,
      error: state.error,
      lastUpdated: state.lastUpdated,
      dateRange: state.dateRange,
      selectedMetrics: state.selectedMetrics,
      fetchAggregate: state.fetchAggregate,
      fetchPredictions: state.fetchPredictions,
      fetchLiveMetrics: state.fetchLiveMetrics,
      refreshAnalytics: state.refreshAnalytics,
      setAggregate: state.setAggregate,
      setPredictions: state.setPredictions,
      setLiveMetrics: state.setLiveMetrics,
      setLoading: state.setLoading,
      setError: state.setError,
      setDateRange: state.setDateRange,
      setSelectedMetrics: state.setSelectedMetrics,
      resetFilters: state.resetFilters,
    }),
    shallow
  );
}

/** Marketing Slice */
export function useMarketingStore() {
  return useDashboardStore(
    (state) => ({
      campaigns: state.campaigns,
      conversions: state.conversions,
      selectedCampaign: state.selectedCampaign,
      loading: state.loading,
      error: state.error,
      lastUpdated: state.lastUpdated,
      channelFilter: state.channelFilter,
      minROI: state.minROI,
      dateRange: state.dateRange,
      pagination: state.pagination,
      fetchCampaigns: state.fetchCampaigns,
      fetchConversions: state.fetchConversions,
      refreshMarketing: state.refreshMarketing,
      setCampaigns: state.setCampaigns,
      setConversions: state.setConversions,
      setSelectedCampaign: state.setSelectedCampaign,
      setLoading: state.setLoading,
      setError: state.setError,
      setChannelFilter: state.setChannelFilter,
      setMinROI: state.setMinROI,
      setDateRange: state.setDateRange,
      setPagination: state.setPagination,
      resetFilters: state.resetFilters,
    }),
    shallow
  );
}

/** Optimization Slice */
export function useOptimizationStore() {
  return useDashboardStore(
    (state) => ({
      recommendations: state.recommendations,
      metrics: state.metrics,
      activeOptimizations: state.activeOptimizations,
      loading: state.loading,
      error: state.error,
      lastUpdated: state.lastUpdated,
      typeFilter: state.typeFilter,
      impactFilter: state.impactFilter,
      statusFilter: state.statusFilter,
      fetchRecommendations: state.fetchRecommendations,
      fetchMetrics: state.fetchMetrics,
      refreshOptimization: state.refreshOptimization,
      applyRecommendation: state.applyRecommendation,
      rejectRecommendation: state.rejectRecommendation,
      setRecommendations: state.setRecommendations,
      setMetrics: state.setMetrics,
      setActiveOptimizations: state.setActiveOptimizations,
      setLoading: state.setLoading,
      setError: state.setError,
      setTypeFilter: state.setTypeFilter,
      setImpactFilter: state.setImpactFilter,
      setStatusFilter: state.setStatusFilter,
      resetFilters: state.resetFilters,
    }),
    shallow
  );
}

/** Forecasting Slice */
export function useForecastingStore() {
  return useDashboardStore(
    (state) => ({
      forecasts: state.forecasts,
      selectedForecast: state.selectedForecast,
      metrics: state.metrics,
      loading: state.loading,
      error: state.error,
      lastUpdated: state.lastUpdated,
      horizon: state.horizon,
      selectedProductIds: state.selectedProductIds,
      dateRange: state.dateRange,
      modelType: state.modelType,
      fetchProductForecast: state.fetchProductForecast,
      fetchMultipleForecasts: state.fetchMultipleForecasts,
      fetchForecastMetrics: state.fetchForecastMetrics,
      refreshForecasting: state.refreshForecasting,
      setForecasts: state.setForecasts,
      setSelectedForecast: state.setSelectedForecast,
      setMetrics: state.setMetrics,
      setLoading: state.setLoading,
      setError: state.setError,
      setHorizon: state.setHorizon,
      setSelectedProductIds: state.setSelectedProductIds,
      setDateRange: state.setDateRange,
      setModelType: state.setModelType,
      resetConfiguration: state.resetConfiguration,
    }),
    shallow
  );
}

/** Nutrition Intelligence Slice */
export function useNutritionIntelligenceStore() {
  return useDashboardStore(
    (state) => ({
      insights: state.insights,
      productData: state.productData,
      trends: state.trends,
      selectedProduct: state.selectedProduct,
      loading: state.loading,
      error: state.error,
      lastUpdated: state.lastUpdated,
      typeFilter: state.typeFilter,
      categoryFilter: state.categoryFilter,
      impactFilter: state.impactFilter,
      searchQuery: state.searchQuery,
      fetchInsights: state.fetchInsights,
      fetchProductData: state.fetchProductData,
      fetchTrends: state.fetchTrends,
      refreshNutritionIntelligence: state.refreshNutritionIntelligence,
      setInsights: state.setInsights,
      setProductData: state.setProductData,
      setTrends: state.setTrends,
      setSelectedProduct: state.setSelectedProduct,
      setLoading: state.setLoading,
      setError: state.setError,
      setTypeFilter: state.setTypeFilter,
      setCategoryFilter: state.setCategoryFilter,
      setImpactFilter: state.setImpactFilter,
      setSearchQuery: state.setSearchQuery,
      resetFilters: state.resetFilters,
    }),
    shallow
  );
}

/** AI Insights Slice */
/* ---------------------------
   Store singletons for direct actions
--------------------------- */
export const analyticsStore = dashboardStore;
export const marketingStore = dashboardStore;
export const optimizationStore = dashboardStore;
export const forecastingStore = dashboardStore;
export const nutritionStore = dashboardStore;

/* ---------------------------
   Dashboard common actions
--------------------------- */
export function useDashboardActions() {
  return useDashboardStore((state) => ({
    setData: state.setData,
    updateKPI: state.updateKPI,
  }));
}

export function useAIInsightsStore() {
  return {
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
    fetchClusters: async () => {},
    fetchClusterDistribution: async () => {},
    fetchClusterInsights: async () => {},
    setSelectedCluster: () => {},
    fetchAnomalies: async () => {},
    fetchAnomalySummary: async () => {},
    detectSalesAnomalies: async () => {},
    fetchForecast: async () => {},
    fetchModelForecast: async () => {},
    setSelectedForecast: () => {},
    fetchRecommendations: async () => {},
    fetchModelRecommendations: async () => {},
    setCurrentDataset: async () => {},
    refreshAIInsights: async () => {},
    setClusters: () => {},
    setAnomalies: () => {},
    setForecasts: () => {},
    setRecommendations: () => {},
    setLoading: () => {},
    setError: () => {},
  };
}
