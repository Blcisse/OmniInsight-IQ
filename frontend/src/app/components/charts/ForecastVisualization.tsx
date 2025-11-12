"use client";
import React, { useMemo } from "react";
import { useFetchData } from "@/app/lib/useFetchData";

type ForecastPoint = { date: string; predicted_sales: number };
type PredictResponse = { forecast: ForecastPoint[] };

export default function ForecastVisualization({ horizon = 7 }: { horizon?: number }) {
  const { data, loading, error, refetch } = useFetchData<PredictResponse>(`/api/analytics/predict?horizon_days=${horizon}`);

  const points = useMemo(() => data?.forecast ?? [], [data]);
  const max = Math.max(...points.map((p) => p.predicted_sales), 1);

  if (loading) return <div>Loading forecast…</div>;
  if (error) return <div style={{ color: "red" }}>{error}</div>;

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h3>Forecast ({horizon} days)</h3>
        <button onClick={refetch}>Refresh</button>
      </div>
      <div style={{ display: "flex", alignItems: "flex-end", gap: 6, height: 160, padding: 6, border: "1px solid #e2e8f0", borderRadius: 8 }}>
        {points.map((p) => (
          <div key={p.date} title={`${p.date}: ${p.predicted_sales.toFixed(2)}`} style={{ width: 20, background: "#6366f1", height: `${(p.predicted_sales / max) * 100}%` }} />
        ))}
      </div>
    </div>
  );
}

