"use client";
import React, { useEffect, useRef } from "react";
import { useDashboardStore } from "@/store/dashboardStore";

export default function SalesOverviewChart() {
  const aggregate = useDashboardStore((state) => state.aggregate);
  const loading = useDashboardStore((state) => state.loading);
  const error = useDashboardStore((state) => state.error);
  const fetchAggregate = useDashboardStore((state) => state.fetchAggregate);
  const hasFetched = useRef(false);

  useEffect(() => {
    // Fetch data only once if not already loaded
    if (!aggregate && !loading && !hasFetched.current) {
      hasFetched.current = true;
      fetchAggregate();
    }
  }, [aggregate, loading, fetchAggregate]);

  const points = aggregate?.by_day ?? [];
  const max = Math.max(...points.map((p) => p.sales), 1);

  if (loading) return <div>Loading sales overview…</div>;
  if (error) return <div style={{ color: "red" }}>{error}</div>;

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h3>Sales Overview</h3>
        <button onClick={() => fetchAggregate()}>Refresh</button>
      </div>
      <div style={{ display: "flex", alignItems: "flex-end", gap: 6, height: 160, padding: 6, border: "1px solid #e2e8f0", borderRadius: 8 }}>
        {points.map((p) => (
          <div key={p.date} title={`${p.date}: ${p.sales.toFixed(2)}`} style={{ width: 20, background: "#22c55e", height: `${(p.sales / max) * 100}%` }} />
        ))}
      </div>
    </div>
  );
}

