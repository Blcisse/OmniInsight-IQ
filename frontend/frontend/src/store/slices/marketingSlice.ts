import type { StateCreator } from "zustand";
import { getCampaignMetrics, getConversions, type CampaignQuery as CampaignFilters, type ConversionQuery as ConversionFilters } from "@/api/marketingApi";
import {
  mockMarketingCampaigns,
  mockMarketingConversions,
} from "../utils/mockData";

/**
 * Marketing data types
 */
export type CampaignMetric = {
  id: number;
  campaign_id?: number;
  campaign_name?: string;
  name?: string;
  channel: string;
  budget: number;
  spend: number;
  impressions: number;
  clicks: number;
  ctr: number;
  cpc: number;
  roi?: number;
  start_date?: string;
  end_date?: string;
};

export type ConversionDatum = {
  campaign_id: number;
  date: string;
  conversions: number;
  revenue: number;
};

export type MarketingState = {
  // Data
  campaigns: CampaignMetric[];
  conversions: ConversionDatum[];
  selectedCampaign: CampaignMetric | null;

  // UI State
  loading: boolean;
  error: string | null;
  lastUpdated: number | null;

  // Filters
  channelFilter: string | null;
  minROI: number | null;
  dateRange: { start: string | null; end: string | null };
  pagination: { limit: number; offset: number; total: number | null };
};

export type MarketingActions = {
  // Data fetching
  fetchCampaigns: (filters?: CampaignFilters) => Promise<void>;
  fetchConversions: (filters?: ConversionFilters) => Promise<void>;
  refreshMarketing: () => Promise<void>;

  // State updates
  setCampaigns: (campaigns: CampaignMetric[]) => void;
  setConversions: (conversions: ConversionDatum[]) => void;
  setSelectedCampaign: (campaign: CampaignMetric | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;

  // Filters
  setChannelFilter: (channel: string | null) => void;
  setMinROI: (roi: number | null) => void;
  setDateRange: (start: string | null, end: string | null) => void;
  setPagination: (limit: number, offset: number, total?: number) => void;
  resetFilters: () => void;
};

export type MarketingSlice = MarketingState & MarketingActions;

const initialState: MarketingState = {
  campaigns: [],
  conversions: [],
  selectedCampaign: null,
  loading: false,
  error: null,
  lastUpdated: null,
  channelFilter: null,
  minROI: null,
  dateRange: { start: null, end: null },
  pagination: { limit: 50, offset: 0, total: null },
};

export const createMarketingSlice: StateCreator<MarketingSlice> = (set, get) => ({
  ...initialState,

  fetchCampaigns: async (filters: CampaignFilters = {}) => {
    set({ loading: true, error: null });
    try {
      const params: CampaignFilters = {};
      if (filters.channel !== undefined) params.channel = filters.channel;
      if (filters.minROI !== undefined) params.minROI = filters.minROI;
      if (filters.limit !== undefined) params.limit = filters.limit;
      if (filters.offset !== undefined) params.offset = filters.offset;

      const response = await getCampaignMetrics(params);
      if (!response.ok) {
        throw Object.assign(new Error(response.error || "Failed to fetch campaigns"), {
          status: response.status,
        });
      }
      const data = response.data;
      set({
        campaigns: data,
        loading: false,
        lastUpdated: Date.now(),
      });
    } catch (error: any) {
      if (error?.status === 404) {
        set({
          campaigns: mockMarketingCampaigns,
          loading: false,
          error: null,
          lastUpdated: Date.now(),
        });
        return;
      }
      set({
        error: error?.message || "Failed to fetch campaigns",
        loading: false,
      });
    }
  },

  fetchConversions: async (filters: ConversionFilters = {}) => {
    set({ loading: true, error: null });
    try {
      const params: ConversionFilters = {};
      if (filters.startDate !== undefined) params.startDate = filters.startDate;
      if (filters.endDate !== undefined) params.endDate = filters.endDate;
      if (filters.limit !== undefined) params.limit = filters.limit;
      if (filters.offset !== undefined) params.offset = filters.offset;

      const response = await getConversions(params);
      if (!response.ok) {
        throw Object.assign(new Error(response.error || "Failed to fetch conversions"), {
          status: response.status,
        });
      }
      const data = response.data;
      set({
        conversions: data,
        loading: false,
        lastUpdated: Date.now(),
      });
    } catch (error: any) {
      if (error?.status === 404) {
        set({
          conversions: mockMarketingConversions,
          loading: false,
          error: null,
          lastUpdated: Date.now(),
        });
        return;
      }
      set({
        error: error?.message || "Failed to fetch conversions",
        loading: false,
      });
    }
  },

  refreshMarketing: async () => {
    // Clear existing data to prevent duplication, then fetch fresh
    set({ loading: true, error: null, campaigns: [], conversions: [] });
    const { fetchCampaigns, fetchConversions, channelFilter, minROI, pagination, dateRange } = get();
    try {
      const campaignParams: CampaignFilters = {
        limit: pagination.limit,
        offset: pagination.offset,
      };
      if (channelFilter) campaignParams.channel = channelFilter;
      if (minROI !== null) campaignParams.minROI = minROI;

      const conversionParams: ConversionFilters = {
        limit: pagination.limit,
        offset: pagination.offset,
      };
      if (dateRange.start) conversionParams.startDate = dateRange.start;
      if (dateRange.end) conversionParams.endDate = dateRange.end;

      await Promise.all([fetchCampaigns(campaignParams), fetchConversions(conversionParams)]);
    } catch (error: any) {
      set({
        error: error?.message || "Failed to refresh marketing data",
        loading: false,
      });
    }
  },

  setCampaigns: (campaigns) => set({ campaigns, lastUpdated: Date.now() }),
  setConversions: (conversions) => set({ conversions, lastUpdated: Date.now() }),
  setSelectedCampaign: (campaign) => set({ selectedCampaign: campaign }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  setChannelFilter: (channel) => set({ channelFilter: channel }),
  setMinROI: (roi) => set({ minROI: roi }),
  setDateRange: (start, end) => set({ dateRange: { start, end } }),
  setPagination: (limit, offset, total) =>
    set({
      pagination: { limit, offset, total: total ?? null },
    }),
  resetFilters: () =>
    set({
      channelFilter: null,
      minROI: null,
      dateRange: { start: null, end: null },
      pagination: { limit: 50, offset: 0, total: null },
    }),
});
