"use client";
import React, { useEffect, useState } from "react";

type LiveSummary = {
  window: string;
  since: string;
  total_revenue: number;
  orders_count: number;
  avg_order_value: number;
};

export default function LiveUpdateWidget({ window = "24h" }: { window?: "24h" | "7d" }) {
  const [data, setData] = useState<LiveSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    try {
      setLoading(true);
      const res = await fetch(`/api/analytics/live?window=${window}`);
      if (!res.ok) throw new Error("Failed to load live data");
      const json = await res.json();
      setData(json);
      setError(null);
    } catch (e: any) {
      setError(e?.message || "Error loading data");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    const t = setInterval(load, 15000); // refresh every 15s
    return () => clearInterval(t);
  }, [window]);

  if (loading) return <div>Loading live summary…</div>;
  if (error) return <div style={{ color: "red" }}>{error}</div>;
  if (!data) return null;

  return (
    <div style={{ border: "1px solid #e2e8f0", borderRadius: 8, padding: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
        <strong>Live Summary ({data.window})</strong>
        <button onClick={load}>Refresh</button>
      </div>
      <div style={{ display: "flex", gap: 16 }}>
        <Stat label="Total Revenue" value={`$${data.total_revenue.toFixed(2)}`} />
        <Stat label="Orders" value={data.orders_count.toString()} />
        <Stat label="Avg Order Value" value={`$${data.avg_order_value.toFixed(2)}`} />
      </div>
      <div style={{ marginTop: 8, color: "#64748b", fontSize: 12 }}>Since {data.since}</div>
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

