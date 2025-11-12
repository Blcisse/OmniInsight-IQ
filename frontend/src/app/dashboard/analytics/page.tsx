"use client";
import React, { useEffect, useState } from "react";
import SalesOverviewChart from "@/app/components/charts/SalesOverviewChart";
import ForecastVisualization from "@/app/components/charts/ForecastVisualization";
import KPICard from "@/app/components/cards/KPICard";

type Aggregate = {
  total_sales: number;
  avg_order_value: number;
  orders_count: number;
  by_day: { date: string; sales: number }[];
};

export default function AnalyticsPage() {
  const [agg, setAgg] = useState<Aggregate | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const res = await fetch("/api/analytics");
        if (!res.ok) throw new Error("Failed to load analytics");
        setAgg(await res.json());
        setError(null);
      } catch (e: any) {
        setError(e?.message || "Error loading analytics");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <section>
      <h1>Analytics</h1>
      {loading && <p>Loading…</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {agg && (
        <>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, marginTop: 12 }}>
            <KPICard label="Total Sales" value={`$${agg.total_sales.toFixed(2)}`} />
            <KPICard label="Avg Order Value" value={`$${agg.avg_order_value.toFixed(2)}`} />
            <KPICard label="Orders" value={agg.orders_count} />
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginTop: 16 }}>
            <SalesOverviewChart />
            <ForecastVisualization />
          </div>
        </>
      )}
    </section>
  );
}

