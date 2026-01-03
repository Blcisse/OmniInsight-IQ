/**
 * Test utilities for verifying state propagation across pages and widgets
 */

import { renderHook, act } from "@testing-library/react";
import { useDashboardStore } from "../dashboardStore";
import { useAnalyticsStore, useMarketingStore } from "../hooks";

describe("Dashboard Store State Propagation", () => {
  beforeEach(() => {
    // Reset store state before each test
    const store = useDashboardStore.getState();
    // Reset all slices to initial state
    if (store.setAggregate) store.setAggregate(null);
    if (store.setCampaigns) store.setCampaigns([]);
    if (store.setLoading) {
      store.setLoading("analytics", false);
      store.setLoading("marketing", false);
    }
    if (store.setError) {
      store.setError("analytics", null);
      store.setError("marketing", null);
    }
  });

  describe("Common Actions", () => {
    it("should set data for analytics slice", () => {
      const { result } = renderHook(() => useDashboardStore());
      
      act(() => {
        result.current.setData("analytics", {
          aggregate: {
            total_sales: 1000,
            avg_order_value: 50,
            orders_count: 20,
            by_day: [],
          },
        });
      });

      const analytics = useDashboardStore.getState();
      expect(analytics.aggregate?.total_sales).toBe(1000);
      expect(analytics.aggregate?.orders_count).toBe(20);
    });

    it("should set data for marketing slice", () => {
      const { result } = renderHook(() => useDashboardStore());
      
      act(() => {
        result.current.setData("marketing", {
          campaigns: [
            {
              id: 1,
              campaign_name: "Test Campaign",
              channel: "Social",
              budget: 1000,
              spend: 500,
              impressions: 10000,
              clicks: 100,
              ctr: 0.01,
              cpc: 5,
            },
          ],
        });
      });

      const marketing = useDashboardStore.getState();
      expect(marketing.campaigns).toHaveLength(1);
      expect(marketing.campaigns[0].campaign_name).toBe("Test Campaign");
    });

    it("should update KPI for analytics slice", () => {
      const { result } = renderHook(() => useDashboardStore());
      
      // First set initial aggregate
      act(() => {
        result.current.setData("analytics", {
          aggregate: {
            total_sales: 1000,
            avg_order_value: 50,
            orders_count: 20,
            by_day: [],
          },
        });
      });

      // Then update KPI
      act(() => {
        result.current.updateKPI("analytics", {
          label: "Total Sales",
          value: 2000,
        });
      });

      const analytics = useDashboardStore.getState();
      expect(analytics.aggregate?.total_sales).toBe(2000);
    });

    it("should set loading state for any slice", () => {
      const { result } = renderHook(() => useDashboardStore());
      
      act(() => {
        result.current.setLoading("analytics", true);
      });

      const analytics = useDashboardStore.getState();
      expect(analytics.loading).toBe(true);

      act(() => {
        result.current.setLoading("analytics", false);
      });

      expect(analytics.loading).toBe(false);
    });

    it("should set error state for any slice", () => {
      const { result } = renderHook(() => useDashboardStore());
      
      act(() => {
        result.current.setError("marketing", "Test error");
      });

      const marketing = useDashboardStore.getState();
      expect(marketing.error).toBe("Test error");

      act(() => {
        result.current.setError("marketing", null);
      });

      expect(marketing.error).toBeNull();
    });
  });

  describe("State Propagation Across Hooks", () => {
    it("should propagate state changes to analytics hook", () => {
      const { result: storeResult } = renderHook(() => useDashboardStore());
      const { result: analyticsResult } = renderHook(() => useAnalyticsStore());

      act(() => {
        storeResult.current.setData("analytics", {
          aggregate: {
            total_sales: 5000,
            avg_order_value: 100,
            orders_count: 50,
            by_day: [],
          },
        });
      });

      expect(analyticsResult.current.aggregate?.total_sales).toBe(5000);
      expect(analyticsResult.current.aggregate?.orders_count).toBe(50);
    });

    it("should propagate state changes to marketing hook", () => {
      const { result: storeResult } = renderHook(() => useDashboardStore());
      const { result: marketingResult } = renderHook(() => useMarketingStore());

      act(() => {
        storeResult.current.setData("marketing", {
          campaigns: [
            {
              id: 1,
              campaign_name: "Campaign 1",
              channel: "Email",
              budget: 2000,
              spend: 1500,
              impressions: 20000,
              clicks: 200,
              ctr: 0.01,
              cpc: 7.5,
            },
          ],
        });
      });

      expect(marketingResult.current.campaigns).toHaveLength(1);
      expect(marketingResult.current.campaigns[0].campaign_name).toBe("Campaign 1");
    });

    it("should update state from multiple hooks simultaneously", () => {
      const { result: analyticsResult } = renderHook(() => useAnalyticsStore());
      const { result: marketingResult } = renderHook(() => useMarketingStore());

      act(() => {
        analyticsResult.current.setAggregate({
          total_sales: 3000,
          avg_order_value: 75,
          orders_count: 40,
          by_day: [],
        });
        marketingResult.current.setCampaigns([
          {
            id: 2,
            campaign_name: "Campaign 2",
            channel: "Search",
            budget: 3000,
            spend: 2000,
            impressions: 30000,
            clicks: 300,
            ctr: 0.01,
            cpc: 6.67,
          },
        ]);
      });

      expect(analyticsResult.current.aggregate?.total_sales).toBe(3000);
      expect(marketingResult.current.campaigns).toHaveLength(1);
      expect(marketingResult.current.campaigns[0].id).toBe(2);
    });
  });

  describe("Loading and Error State Management", () => {
    it("should handle loading states independently per slice", () => {
      const { result: analyticsResult } = renderHook(() => useAnalyticsStore());
      const { result: marketingResult } = renderHook(() => useMarketingStore());

      act(() => {
        analyticsResult.current.setLoading(true);
        marketingResult.current.setLoading(false);
      });

      expect(analyticsResult.current.loading).toBe(true);
      expect(marketingResult.current.loading).toBe(false);
    });

    it("should handle error states independently per slice", () => {
      const { result: analyticsResult } = renderHook(() => useAnalyticsStore());
      const { result: marketingResult } = renderHook(() => useMarketingStore());

      act(() => {
        analyticsResult.current.setError("Analytics error");
        marketingResult.current.setError("Marketing error");
      });

      expect(analyticsResult.current.error).toBe("Analytics error");
      expect(marketingResult.current.error).toBe("Marketing error");
    });
  });
});

