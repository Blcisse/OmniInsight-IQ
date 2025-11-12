"use client";
import React from "react";
import { useFetchData } from "@/app/lib/useFetchData";

type Point = { date: string; sales: number };
type Aggregate = { by_day: Point[] };

export default function SalesOverviewChart() {
  const { data, loading, error, refetch } = useFetchData<Aggregate>("/api/analytics");

  if (loading) return <div>Loading sales overview…</div>;
  if (error) return <div style={{ color: "red" }}>{error}</div>;
  const points = data?.by_day ?? [];
  const max = Math.max(...points.map((p) => p.sales), 1);

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h3>Sales Overview</h3>
        <button onClick={refetch}>Refresh</button>
      </div>
      <div style={{ display: "flex", alignItems: "flex-end", gap: 6, height: 160, padding: 6, border: "1px solid #e2e8f0", borderRadius: 8 }}>
        {points.map((p) => (
          <div key={p.date} title={`${p.date}: ${p.sales.toFixed(2)}`} style={{ width: 20, background: "#22c55e", height: `${(p.sales / max) * 100}%` }} />
        ))}
      </div>
    </div>
  );
}

