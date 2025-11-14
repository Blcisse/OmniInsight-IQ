"use client";
import React, { useEffect } from "react";
import { useAnalyticsStore } from "@/store/hooks";

export default function SalesOverviewChart() {
  const analytics = useAnalyticsStore();

  useEffect(() => {
    // Fetch data if not already loaded
    if (!analytics.aggregate && !analytics.loading) {
      analytics.fetchAggregate();
    }
  }, [analytics]);

  const points = analytics.aggregate?.by_day ?? [];
  const max = Math.max(...points.map((p) => p.sales), 1);

  if (analytics.loading) return <div>Loading sales overview…</div>;
  if (analytics.error) return <div style={{ color: "red" }}>{analytics.error}</div>;

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h3>Sales Overview</h3>
        <button onClick={() => analytics.fetchAggregate()}>Refresh</button>
      </div>
      <div style={{ display: "flex", alignItems: "flex-end", gap: 6, height: 160, padding: 6, border: "1px solid #e2e8f0", borderRadius: 8 }}>
        {points.map((p) => (
          <div key={p.date} title={`${p.date}: ${p.sales.toFixed(2)}`} style={{ width: 20, background: "#22c55e", height: `${(p.sales / max) * 100}%` }} />
        ))}
      </div>
    </div>
  );
}

