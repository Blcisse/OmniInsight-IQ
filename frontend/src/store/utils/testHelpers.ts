/**
 * Test helper utilities for dashboard store testing
 */

import { useDashboardStore } from "../dashboardStore";
import type { DashboardStore, SliceName, KPIData } from "../dashboardStore";

/**
 * Reset all store state to initial values
 */
export function resetStore() {
  const store = useDashboardStore.getState();
  
  // Reset analytics
  if (store.setAggregate) store.setAggregate(null);
  if (store.setPredictions) store.setPredictions(null);
  if (store.setLiveMetrics) store.setLiveMetrics(null);
  
  // Reset marketing
  if (store.setCampaigns) store.setCampaigns([]);
  if (store.setConversions) store.setConversions([]);
  
  // Reset optimization
  if (store.setRecommendations) store.setRecommendations([]);
  if (store.setMetrics) store.setMetrics(null);
  
  // Reset forecasting
  if (store.setForecasts) store.setForecasts([]);
  if (store.setMetrics) store.setMetrics(null);
  
  // Reset nutrition intelligence
  if (store.setInsights) store.setInsights([]);
  if (store.setProductData) store.setProductData([]);
  if (store.setTrends) store.setTrends([]);
  
  // Reset loading and error states
  const slices: SliceName[] = ["analytics", "marketing", "optimization", "forecasting", "nutritionIntelligence"];
  slices.forEach((slice) => {
    if (store.setLoading) store.setLoading(slice, false);
    if (store.setError) store.setError(slice, null);
  });
}

/**
 * Get current store state snapshot
 */
export function getStoreSnapshot(): Partial<DashboardStore> {
  const state = useDashboardStore.getState();
  return {
    aggregate: state.aggregate,
    campaigns: state.campaigns,
    loading: state.loading,
    error: state.error,
  };
}

/**
 * Wait for store state to match a condition
 */
export async function waitForStoreCondition(
  condition: (state: DashboardStore) => boolean,
  timeout = 5000
): Promise<void> {
  const startTime = Date.now();
  
  return new Promise((resolve, reject) => {
    const checkCondition = () => {
      const state = useDashboardStore.getState();
      if (condition(state)) {
        resolve();
      } else if (Date.now() - startTime > timeout) {
        reject(new Error("Timeout waiting for store condition"));
      } else {
        setTimeout(checkCondition, 100);
      }
    };
    checkCondition();
  });
}

/**
 * Mock data generators for testing
 */
export const mockData = {
  analytics: {
    aggregate: {
      total_sales: 10000,
      avg_order_value: 50,
      orders_count: 200,
      by_day: [
        { date: "2025-01-01", sales: 1000 },
        { date: "2025-01-02", sales: 1200 },
        { date: "2025-01-03", sales: 1500 },
      ],
    },
    predictions: {
      forecast: [1100, 1300, 1600],
      dates: ["2025-01-04", "2025-01-05", "2025-01-06"],
      confidence: 0.85,
    },
  },
  marketing: {
    campaigns: [
      {
        id: 1,
        campaign_name: "Test Campaign",
        channel: "Social",
        budget: 5000,
        spend: 3000,
        impressions: 50000,
        clicks: 500,
        ctr: 0.01,
        cpc: 6,
        roi: 2.5,
      },
    ],
    conversions: [
      {
        campaign_id: 1,
        date: "2025-01-01",
        conversions: 10,
        revenue: 500,
      },
    ],
  },
};

/**
 * Helper to populate store with mock data
 */
export function populateStoreWithMockData() {
  const store = useDashboardStore.getState();
  
  if (store.setData) {
    store.setData("analytics", mockData.analytics);
    store.setData("marketing", mockData.marketing);
  }
}

/**
 * Verify state propagation between slices
 */
export function verifyStatePropagation(
  sliceName: SliceName,
  expectedData: any
): boolean {
  const state = useDashboardStore.getState();
  
  switch (sliceName) {
    case "analytics":
      return (
        state.aggregate?.total_sales === expectedData.aggregate?.total_sales &&
        state.aggregate?.orders_count === expectedData.aggregate?.orders_count
      );
    case "marketing":
      return (
        state.campaigns.length === expectedData.campaigns?.length &&
        state.campaigns[0]?.campaign_name === expectedData.campaigns?.[0]?.campaign_name
      );
    default:
      return false;
  }
}

