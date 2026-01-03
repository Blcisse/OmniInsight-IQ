import type { StateCreator } from "zustand";
import {
  mockOptimizationMetrics,
  mockOptimizationRecommendations,
} from "../utils/mockData";

/**
 * Optimization data types
 */
export type OptimizationRecommendation = {
  id: string;
  type: "pricing" | "inventory" | "promotion" | "supply_chain" | "other";
  title: string;
  description: string;
  impact: "high" | "medium" | "low";
  estimatedValue: number;
  confidence: number;
  status: "pending" | "applied" | "rejected";
  createdAt: string;
};

export type OptimizationMetrics = {
  currentEfficiency: number;
  targetEfficiency: number;
  improvementPotential: number;
  areas: {
    category: string;
    current: number;
    target: number;
    improvement: number;
  }[];
};

export type OptimizationState = {
  // Data
  recommendations: OptimizationRecommendation[];
  metrics: OptimizationMetrics | null;
  activeOptimizations: string[];

  // UI State
  loading: boolean;
  error: string | null;
  lastUpdated: number | null;

  // Filters
  typeFilter: string | null;
  impactFilter: "high" | "medium" | "low" | null;
  statusFilter: "pending" | "applied" | "rejected" | null;
};

export type OptimizationActions = {
  // Data fetching
  fetchRecommendations: () => Promise<void>;
  fetchMetrics: () => Promise<void>;
  refreshOptimization: () => Promise<void>;

  // Actions
  applyRecommendation: (id: string) => Promise<void>;
  rejectRecommendation: (id: string) => Promise<void>;

  // State updates
  setRecommendations: (recommendations: OptimizationRecommendation[]) => void;
  setMetrics: (metrics: OptimizationMetrics) => void;
  setActiveOptimizations: (ids: string[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;

  // Filters
  setTypeFilter: (type: string | null) => void;
  setImpactFilter: (impact: "high" | "medium" | "low" | null) => void;
  setStatusFilter: (status: "pending" | "applied" | "rejected" | null) => void;
  resetFilters: () => void;
};

export type OptimizationSlice = OptimizationState & OptimizationActions;

const initialState: OptimizationState = {
  recommendations: [],
  metrics: null,
  activeOptimizations: [],
  loading: false,
  error: null,
  lastUpdated: null,
  typeFilter: null,
  impactFilter: null,
  statusFilter: null,
};

export const createOptimizationSlice: StateCreator<OptimizationSlice> = (set, get) => ({
  ...initialState,

  fetchRecommendations: async () => {
    set({ loading: true, error: null });
    try {
      const response = await fetch("/api/optimization/recommendations");
      if (!response.ok) {
        throw Object.assign(new Error("Failed to fetch recommendations"), {
          status: response.status,
        });
      }
      const data = await response.json();
      set({
        recommendations: data,
        loading: false,
        lastUpdated: Date.now(),
      });
    } catch (error: any) {
      if (error?.status === 404) {
        set({
          recommendations: mockOptimizationRecommendations,
          loading: false,
          error: null,
          lastUpdated: Date.now(),
        });
        return;
      }
      set({
        error: error?.message || "Failed to fetch recommendations",
        loading: false,
      });
    }
  },

  fetchMetrics: async () => {
    set({ loading: true, error: null });
    try {
      const response = await fetch("/api/optimization/metrics");
      if (!response.ok) {
        throw Object.assign(new Error("Failed to fetch optimization metrics"), {
          status: response.status,
        });
      }
      const data = await response.json();
      set({
        metrics: data,
        loading: false,
        lastUpdated: Date.now(),
      });
    } catch (error: any) {
      if (error?.status === 404) {
        set({
          metrics: mockOptimizationMetrics,
          loading: false,
          error: null,
          lastUpdated: Date.now(),
        });
        return;
      }
      set({
        error: error?.message || "Failed to fetch optimization metrics",
        loading: false,
      });
    }
  },

  refreshOptimization: async () => {
    // Clear existing data to prevent duplication, then fetch fresh
    set({ loading: true, error: null, recommendations: [] });
    const { fetchRecommendations, fetchMetrics } = get();
    try {
      await Promise.all([fetchRecommendations(), fetchMetrics()]);
    } catch (error: any) {
      set({
        error: error?.message || "Failed to refresh optimization data",
        loading: false,
      });
    }
  },

  applyRecommendation: async (id: string) => {
    try {
      const response = await fetch(`/api/optimization/recommendations/${id}/apply`, {
        method: "POST",
      });
      if (!response.ok && response.status !== 404) throw new Error("Failed to apply recommendation");
      const { recommendations, activeOptimizations } = get();
      set({
        recommendations: recommendations.map((r) =>
          r.id === id ? { ...r, status: "applied" as const } : r
        ),
        activeOptimizations: [...activeOptimizations, id],
      });
    } catch (error: any) {
      set({ error: error?.message || "Failed to apply recommendation" });
    }
  },

  rejectRecommendation: async (id: string) => {
    try {
      const response = await fetch(`/api/optimization/recommendations/${id}/reject`, {
        method: "POST",
      });
      if (!response.ok && response.status !== 404) throw new Error("Failed to reject recommendation");
      const { recommendations } = get();
      set({
        recommendations: recommendations.map((r) =>
          r.id === id ? { ...r, status: "rejected" as const } : r
        ),
      });
    } catch (error: any) {
      set({ error: error?.message || "Failed to reject recommendation" });
    }
  },

  setRecommendations: (recommendations) => set({ recommendations, lastUpdated: Date.now() }),
  setMetrics: (metrics) => set({ metrics, lastUpdated: Date.now() }),
  setActiveOptimizations: (ids) => set({ activeOptimizations: ids }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  setTypeFilter: (type) => set({ typeFilter: type }),
  setImpactFilter: (impact) => set({ impactFilter: impact }),
  setStatusFilter: (status) => set({ statusFilter: status }),
  resetFilters: () =>
    set({
      typeFilter: null,
      impactFilter: null,
      statusFilter: null,
    }),
});
