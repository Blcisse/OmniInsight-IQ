export const mockAnalyticsAggregate = {
  total_sales: 245000.5,
  avg_order_value: 189.75,
  orders_count: 1290,
  revenue_growth_pct: 8.4,
  by_day: Array.from({ length: 7 }).map((_, idx) => {
    const date = new Date();
    date.setDate(date.getDate() - (6 - idx));
    return {
      date: date.toISOString().slice(0, 10),
      sales: 25000 + idx * 1200,
    };
  }),
};

export const mockAnalyticsPredictions = {
  forecast: [26000, 26800, 27450, 28120, 28900],
  dates: Array.from({ length: 5 }).map((_, idx) => {
    const date = new Date();
    date.setDate(date.getDate() + idx + 1);
    return date.toISOString().slice(0, 10);
  }),
  confidence: 0.84,
};

export const mockAnalyticsLive = {
  revenue_last_24h: 48000,
  orders_last_24h: 320,
  avg_order_value: 150,
};

export const mockMarketingCampaigns = [
  {
    id: 1,
    campaign_name: "Awareness Boost",
    channel: "Social",
    budget: 25000,
    spend: 18000,
    impressions: 120000,
    clicks: 8500,
    ctr: 0.07,
    cpc: 2.11,
    roi: 3.4,
  },
  {
    id: 2,
    campaign_name: "Search Intent",
    channel: "Search",
    budget: 18000,
    spend: 15000,
    impressions: 98000,
    clicks: 10400,
    ctr: 0.106,
    cpc: 1.44,
    roi: 4.1,
  },
];

export const mockMarketingConversions = [
  {
    campaign_id: 1,
    date: new Date().toISOString().slice(0, 10),
    conversions: 320,
    revenue: 68000,
  },
  {
    campaign_id: 2,
    date: new Date().toISOString().slice(0, 10),
    conversions: 410,
    revenue: 82000,
  },
];

export const mockOptimizationMetrics = {
  currentEfficiency: 0.64,
  targetEfficiency: 0.82,
  improvementPotential: 0.18,
  areas: [
    { category: "Pricing", current: 0.58, target: 0.8, improvement: 0.22 },
    { category: "Inventory", current: 0.62, target: 0.78, improvement: 0.16 },
    { category: "Logistics", current: 0.67, target: 0.85, improvement: 0.18 },
  ],
};

export const mockOptimizationRecommendations = [
  {
    id: "rec-1",
    type: "pricing" as const,
    title: "Adjust premium bundle pricing",
    description: "Increase bundle price by 6% to align with competitor median pricing.",
    impact: "high" as const,
    estimatedValue: 42000,
    confidence: 0.82,
    status: "pending" as const,
    createdAt: new Date().toISOString(),
  },
  {
    id: "rec-2",
    type: "inventory" as const,
    title: "Reallocate stock to NA warehouse",
    description: "Shift 15% of slow-moving EU inventory to NA to meet demand surge.",
    impact: "medium" as const,
    estimatedValue: 18000,
    confidence: 0.76,
    status: "pending" as const,
    createdAt: new Date().toISOString(),
  },
];
