"use client";
import React, { useEffect, useMemo } from "react";
import { useAnalyticsStore } from "@/store/hooks";

export default function ForecastVisualization({ horizon = 7 }: { horizon?: number }) {
  const analytics = useAnalyticsStore();

  useEffect(() => {
    // Fetch predictions if not already loaded
    if (!analytics.predictions && !analytics.loading) {
      analytics.fetchPredictions(horizon);
    }
  }, [analytics, horizon]);

  const points = useMemo(() => {
    if (!analytics.predictions) return [];
    return analytics.predictions.forecast?.map((value, index) => ({
      date: analytics.predictions?.dates?.[index] || `Day ${index + 1}`,
      predicted_sales: value,
    })) ?? [];
  }, [analytics.predictions]);
  
  const max = Math.max(...points.map((p) => p.predicted_sales), 1);

  if (analytics.loading) return <div>Loading forecast…</div>;
  if (analytics.error) return <div style={{ color: "red" }}>{analytics.error}</div>;

  return (
    <div className="glass-card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
        <h3>Forecast ({horizon} days)</h3>
        <button
          className="interactive-button"
          data-size="small"
          onClick={() => analytics.fetchPredictions(horizon)}
        >
          Refresh
        </button>
      </div>
      <div style={{ display: "flex", alignItems: "flex-end", gap: 6, height: 160, padding: 6 }}>
        {points.map((p, i) => (
          <div
            key={p.date || i}
            title={`${p.date}: ${p.predicted_sales.toFixed(2)}`}
            style={{
              width: 20,
              background: "var(--gradient-gr1)",
              height: `${(p.predicted_sales / max) * 100}%`,
              borderRadius: 6,
              boxShadow: "0 6px 12px rgba(20, 199, 208, 0.35)",
            }}
          />
        ))}
      </div>
    </div>
  );
}
