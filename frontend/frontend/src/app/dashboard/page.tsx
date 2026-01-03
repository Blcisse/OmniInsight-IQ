"use client";
import React, { useEffect, useRef } from "react";
import { useDashboardStore } from "@/store/dashboardStore";
import LoadingState from "@/components/LoadingState";
import ErrorDisplay from "@/components/ErrorDisplay";
import RetryButton from "@/components/RetryButton";
import PodContainer from "@/components/containers/PodContainer";

export default function DashboardPage() {
  // Individual selectors to avoid infinite loops
  const aggregate = useDashboardStore((state) => state.aggregate);
  const campaigns = useDashboardStore((state) => state.campaigns);
  const loading = useDashboardStore((state) => state.loading);
  const error = useDashboardStore((state) => state.error);
  const fetchAggregate = useDashboardStore((state) => state.fetchAggregate);
  const fetchCampaigns = useDashboardStore((state) => state.fetchCampaigns);
  const refreshAnalytics = useDashboardStore((state) => state.refreshAnalytics);
  const refreshMarketing = useDashboardStore((state) => state.refreshMarketing);
  const setError = useDashboardStore((state) => state.setError);

  const hasFetched = useRef(false);

  useEffect(() => {
    if (!hasFetched.current) {
      hasFetched.current = true;
      fetchAggregate();
      fetchCampaigns();
    }
  }, []);

  const handleRetry = () => {
    refreshAnalytics();
    refreshMarketing();
  };

  return (
    <section>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <h1 className="heading-gradient" style={{ fontSize: "2rem", margin: 0 }}>
          Dashboard
        </h1>
        <RetryButton
          onRetry={handleRetry}
          label="Refresh All"
          variant="outline"
          disabled={loading}
        />
      </div>

      <ErrorDisplay
        error={error}
        onRetry={handleRetry}
        variant="card"
        dismissible={true}
        onDismiss={() => setError(null)}
      />

      <LoadingState loading={loading} error={error} message="Loading dashboard data...">

      {aggregate && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "1.5rem", marginTop: "1.5rem" }}>
          <PodContainer padding="lg" variant="elevated">
            <KPI title="Total Sales" value={`$${aggregate.total_sales.toFixed(2)}`} />
          </PodContainer>
          <PodContainer padding="lg" variant="elevated">
            <KPI title="Avg Order Value" value={`$${aggregate.avg_order_value.toFixed(2)}`} />
          </PodContainer>
          <PodContainer padding="lg" variant="elevated">
            <KPI title="Orders" value={aggregate.orders_count.toString()} />
          </PodContainer>
        </div>
      )}

      {aggregate && (
        <div style={{ marginTop: 24 }}>
          <h2>Sales (Last 7 Days)</h2>
          <MiniChart data={aggregate.by_day.map((d) => d.sales)} labels={aggregate.by_day.map((d) => d.date.slice(5))} />
        </div>
      )}

      {campaigns.length > 0 && (
        <PodContainer
          title="Top Campaigns"
          padding="lg"
          variant="default"
          style={{ marginTop: "1.5rem" }}
        >
          <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
            {campaigns.slice(0, 5).map((c) => (
              <li
                key={c.id || c.campaign_id}
                style={{
                  padding: "0.75rem 0",
                  borderBottom: "1px solid var(--glass-border)",
                  color: "var(--text-secondary)",
                }}
              >
                <strong style={{ color: "var(--text-primary)" }}>
                  {c.campaign_name || c.name || `Campaign ${c.id}`}
                </strong>{" "}
                — {c.impressions.toLocaleString()} imp · {c.clicks.toLocaleString()} clicks · CTR{" "}
                {(c.ctr * 100).toFixed(2)}%
              </li>
            ))}
          </ul>
        </PodContainer>
      )}
      </LoadingState>
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

