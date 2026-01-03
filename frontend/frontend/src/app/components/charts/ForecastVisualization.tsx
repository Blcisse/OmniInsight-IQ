"use client";
import React, { useEffect, useMemo, useRef } from "react";
import { useDashboardStore } from "@/store/dashboardStore";

export default function ForecastVisualization({ horizon = 7 }: { horizon?: number }) {
  const predictions = useDashboardStore((state) => state.predictions);
  const loading = useDashboardStore((state) => state.loading);
  const error = useDashboardStore((state) => state.error);
  const fetchPredictions = useDashboardStore((state) => state.fetchPredictions);
  const hasFetched = useRef(false);

  useEffect(() => {
    // Fetch predictions only once if not already loaded
    if (!predictions && !loading && !hasFetched.current) {
      hasFetched.current = true;
      fetchPredictions(horizon);
    }
  }, [predictions, loading, fetchPredictions, horizon]);

  const points = useMemo(() => {
    if (!predictions) return [];
    return predictions.forecast?.map((value, index) => ({
      date: predictions?.dates?.[index] || `Day ${index + 1}`,
      predicted_sales: value,
    })) ?? [];
  }, [predictions]);
  
  const max = Math.max(...points.map((p) => p.predicted_sales), 1);

  if (loading) return <div>Loading forecast…</div>;
  if (error) return <div style={{ color: "red" }}>{error}</div>;

  return (
    <div className="glass-card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
        <h3>Forecast ({horizon} days)</h3>
        <button
          className="interactive-button"
          data-size="small"
          onClick={() => fetchPredictions(horizon)}
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
