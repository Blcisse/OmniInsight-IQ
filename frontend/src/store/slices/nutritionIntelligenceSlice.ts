import type { StateCreator } from "zustand";

/**
 * Nutrition Intelligence data types
 */
export type NutritionInsight = {
  id: string;
  type: "trend" | "recommendation" | "alert" | "opportunity";
  title: string;
  description: string;
  category: string;
  impact: "high" | "medium" | "low";
  confidence: number;
  relatedProducts?: string[];
  createdAt: string;
};

export type ProductNutritionData = {
  productId: string;
  productName: string;
  nutritionScore: number;
  healthMetrics: {
    calories: number;
    protein: number;
    carbs: number;
    fat: number;
    fiber: number;
    sugar: number;
  };
  trends: {
    period: string;
    score: number;
    change: number;
  }[];
  recommendations: string[];
};

export type NutritionTrend = {
  category: string;
  trend: "increasing" | "decreasing" | "stable";
  change: number;
  products: string[];
  period: string;
};

export type NutritionIntelligenceState = {
  // Data
  insights: NutritionInsight[];
  productData: ProductNutritionData[];
  trends: NutritionTrend[];
  selectedProduct: ProductNutritionData | null;

  // UI State
  loading: boolean;
  error: string | null;
  lastUpdated: number | null;

  // Filters
  typeFilter: string | null;
  categoryFilter: string | null;
  impactFilter: "high" | "medium" | "low" | null;
  searchQuery: string;
};

export type NutritionIntelligenceActions = {
  // Data fetching
  fetchInsights: () => Promise<void>;
  fetchProductData: (productId?: string) => Promise<void>;
  fetchTrends: (category?: string) => Promise<void>;
  refreshNutritionIntelligence: () => Promise<void>;

  // State updates
  setInsights: (insights: NutritionInsight[]) => void;
  setProductData: (data: ProductNutritionData[]) => void;
  setTrends: (trends: NutritionTrend[]) => void;
  setSelectedProduct: (product: ProductNutritionData | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;

  // Filters
  setTypeFilter: (type: string | null) => void;
  setCategoryFilter: (category: string | null) => void;
  setImpactFilter: (impact: "high" | "medium" | "low" | null) => void;
  setSearchQuery: (query: string) => void;
  resetFilters: () => void;
};

export type NutritionIntelligenceSlice = NutritionIntelligenceState & NutritionIntelligenceActions;

const initialState: NutritionIntelligenceState = {
  insights: [],
  productData: [],
  trends: [],
  selectedProduct: null,
  loading: false,
  error: null,
  lastUpdated: null,
  typeFilter: null,
  categoryFilter: null,
  impactFilter: null,
  searchQuery: "",
};

export const createNutritionIntelligenceSlice: StateCreator<NutritionIntelligenceSlice> = (set, get) => ({
  ...initialState,

  fetchInsights: async () => {
    set({ loading: true, error: null });
    try {
      const response = await fetch("/api/nutrition-intelligence/insights");
      if (!response.ok) throw new Error("Failed to fetch nutrition insights");
      const data = await response.json();
      set({
        insights: data,
        loading: false,
        lastUpdated: Date.now(),
      });
    } catch (error: any) {
      set({
        error: error?.message || "Failed to fetch nutrition insights",
        loading: false,
      });
    }
  },

  fetchProductData: async (productId?: string) => {
    set({ loading: true, error: null });
    try {
      const url = productId
        ? `/api/nutrition-intelligence/products/${productId}`
        : "/api/nutrition-intelligence/products";
      const response = await fetch(url);
      if (!response.ok) throw new Error("Failed to fetch product nutrition data");
      const data = await response.json();
      set({
        productData: Array.isArray(data) ? data : [data],
        loading: false,
        lastUpdated: Date.now(),
      });
    } catch (error: any) {
      set({
        error: error?.message || "Failed to fetch product nutrition data",
        loading: false,
      });
    }
  },

  fetchTrends: async (category?: string) => {
    set({ loading: true, error: null });
    try {
      const url = category
        ? `/api/nutrition-intelligence/trends?category=${category}`
        : "/api/nutrition-intelligence/trends";
      const response = await fetch(url);
      if (!response.ok) throw new Error("Failed to fetch nutrition trends");
      const data = await response.json();
      set({
        trends: data,
        loading: false,
        lastUpdated: Date.now(),
      });
    } catch (error: any) {
      set({
        error: error?.message || "Failed to fetch nutrition trends",
        loading: false,
      });
    }
  },

  refreshNutritionIntelligence: async () => {
    // Clear existing data to prevent duplication, then fetch fresh
    set({ loading: true, error: null, insights: [], productData: [], trends: [] });
    const { fetchInsights, fetchProductData, fetchTrends, categoryFilter } = get();
    try {
      await Promise.all([
        fetchInsights(),
        fetchProductData(),
        fetchTrends(categoryFilter || undefined),
      ]);
    } catch (error: any) {
      set({
        error: error?.message || "Failed to refresh nutrition intelligence data",
        loading: false,
      });
    }
  },

  setInsights: (insights) => set({ insights, lastUpdated: Date.now() }),
  setProductData: (data) => set({ productData: data, lastUpdated: Date.now() }),
  setTrends: (trends) => set({ trends, lastUpdated: Date.now() }),
  setSelectedProduct: (product) => set({ selectedProduct: product }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  setTypeFilter: (type) => set({ typeFilter: type }),
  setCategoryFilter: (category) => set({ categoryFilter: category }),
  setImpactFilter: (impact) => set({ impactFilter: impact }),
  setSearchQuery: (query) => set({ searchQuery: query }),
  resetFilters: () =>
    set({
      typeFilter: null,
      categoryFilter: null,
      impactFilter: null,
      searchQuery: "",
    }),
});

