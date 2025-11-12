"use client";
import React, { useEffect, useState } from "react";

type Aggregate = {
  total_sales: number;
  avg_order_value: number;
  orders_count: number;
  by_day: { date: string; sales: number }[];
};

type CampaignMetric = {
  campaign_id: number;
  name: string;
  impressions: number;
  clicks: number;
  ctr: number;
  spend: number;
  cpc: number;
};

export default function DashboardPage() {
  const [analytics, setAnalytics] = useState<Aggregate | null>(null);
  const [campaigns, setCampaigns] = useState<CampaignMetric[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const [aRes, mRes] = await Promise.all([
          fetch("/api/analytics"),
          fetch("/api/marketing/campaign-metrics"),
        ]);
        if (!aRes.ok) throw new Error("Failed to load analytics");
        if (!mRes.ok) throw new Error("Failed to load marketing");
        const a = (await aRes.json()) as Aggregate;
        const m = (await mRes.json()) as CampaignMetric[];
        setAnalytics(a);
        setCampaigns(m);
        setError(null);
      } catch (e: any) {
        setError(e?.message || "Error loading data");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <section>
      <h1>Dashboard</h1>
      {loading && <p>Loading…</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {analytics && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, marginTop: 12 }}>
          <KPI title="Total Sales" value={`$${analytics.total_sales.toFixed(2)}`} />
          <KPI title="Avg Order Value" value={`$${analytics.avg_order_value.toFixed(2)}`} />
          <KPI title="Orders" value={analytics.orders_count.toString()} />
        </div>
      )}

      {analytics && (
        <div style={{ marginTop: 24 }}>
          <h2>Sales (Last 7 Days)</h2>
          <MiniChart data={analytics.by_day.map((d) => d.sales)} labels={analytics.by_day.map((d) => d.date.slice(5))} />
        </div>
      )}

      {campaigns.length > 0 && (
        <div style={{ marginTop: 24 }}>
          <h2>Top Campaigns</h2>
          <ul>
            {campaigns.slice(0, 5).map((c) => (
              <li key={c.campaign_id}>
                <strong>{c.name}</strong> — {c.impressions.toLocaleString()} imp · {c.clicks.toLocaleString()} clicks · CTR {(c.ctr).toFixed(2)}%
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}

function KPI({ title, value }: { title: string; value: string }) {
  return (
    <div style={{ padding: 16, border: "1px solid #e2e8f0", borderRadius: 8 }}>
      <div style={{ color: "#64748b", fontSize: 12 }}>{title}</div>
      <div style={{ fontSize: 20, fontWeight: 600 }}>{value}</div>
    </div>
  );
}

function MiniChart({ data, labels }: { data: number[]; labels: string[] }) {
  const max = Math.max(...data, 1);
  return (
    <div style={{ display: "flex", alignItems: "flex-end", gap: 6, height: 120 }}>
      {data.map((v, i) => (
        <div key={i} title={`${labels[i]}: ${v.toFixed(2)}`} style={{ width: 24, background: "#3b82f6", height: `${(v / max) * 100}%` }} />
      ))}
    </div>
  );
}

