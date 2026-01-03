"use client";
import React, { useEffect } from "react";
import { useAnalyticsStore } from "@/store/hooks";

export default function LiveUpdateWidget({ window = "24h" }: { window?: "24h" | "7d" }) {
  const analytics = useAnalyticsStore();

  useEffect(() => {
    analytics.fetchLiveMetrics(window);
    const interval = setInterval(() => {
      analytics.fetchLiveMetrics(window);
    }, 15000); // refresh every 15s
    return () => clearInterval(interval);
  }, [window, analytics.fetchLiveMetrics]);

  const data = analytics.liveMetrics;
  const loading = analytics.loading;
  const error = analytics.error;

  if (loading) return <div>Loading live summary…</div>;
  if (error) return <div style={{ color: "red" }}>{error}</div>;
  if (!data || typeof data !== "object") return null;

  const windowValue = (data.window as string) || window;
  const totalRevenue = typeof data.total_revenue === "number" ? data.total_revenue : 0;
  const ordersCount = typeof data.orders_count === "number" ? data.orders_count : 0;
  const avgOrderValue = typeof data.avg_order_value === "number" ? data.avg_order_value : 0;
  const since = (data.since as string) || "";

  return (
    <div style={{ border: "1px solid #e2e8f0", borderRadius: 8, padding: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
        <strong>Live Summary ({windowValue})</strong>
        <button onClick={() => analytics.fetchLiveMetrics(window)}>Refresh</button>
      </div>
      <div style={{ display: "flex", gap: 16 }}>
        <Stat label="Total Revenue" value={`$${totalRevenue.toFixed(2)}`} />
        <Stat label="Orders" value={ordersCount.toString()} />
        <Stat label="Avg Order Value" value={`$${avgOrderValue.toFixed(2)}`} />
      </div>
      {since && <div style={{ marginTop: 8, color: "#64748b", fontSize: 12 }}>Since {since}</div>}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div style={{ color: "#64748b", fontSize: 12 }}>{label}</div>
      <div style={{ fontSize: 18, fontWeight: 700 }}>{value}</div>
    </div>
  );
}

