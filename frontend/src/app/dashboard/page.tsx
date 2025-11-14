"use client";
import React, { useEffect } from "react";
import { useAnalyticsStore, useMarketingStore } from "@/store/hooks";
import LoadingState from "@/components/LoadingState";
import ErrorDisplay from "@/components/ErrorDisplay";
import RetryButton from "@/components/RetryButton";
import PodContainer from "@/components/containers/PodContainer";

export default function DashboardPage() {
  // Analytics slice
  const analytics = useAnalyticsStore();
  
  // Marketing slice
  const marketing = useMarketingStore();

  const loading = analytics.loading || marketing.loading;
  const error = analytics.error || marketing.error;

  useEffect(() => {
    analytics.fetchAggregate();
    marketing.fetchCampaigns();
  }, [analytics.fetchAggregate, marketing.fetchCampaigns]);

  const handleRetry = () => {
    analytics.refreshAnalytics();
    marketing.refreshMarketing();
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
        onDismiss={() => {
          analytics.setError(null);
          marketing.setError(null);
        }}
      />

      <LoadingState loading={loading} error={error} message="Loading dashboard data...">

      {analytics.aggregate && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "1.5rem", marginTop: "1.5rem" }}>
          <PodContainer padding="lg" variant="elevated">
            <KPI title="Total Sales" value={`$${analytics.aggregate.total_sales.toFixed(2)}`} />
          </PodContainer>
          <PodContainer padding="lg" variant="elevated">
            <KPI title="Avg Order Value" value={`$${analytics.aggregate.avg_order_value.toFixed(2)}`} />
          </PodContainer>
          <PodContainer padding="lg" variant="elevated">
            <KPI title="Orders" value={analytics.aggregate.orders_count.toString()} />
          </PodContainer>
        </div>
      )}

      {analytics.aggregate && (
        <div style={{ marginTop: 24 }}>
          <h2>Sales (Last 7 Days)</h2>
          <MiniChart data={analytics.aggregate.by_day.map((d) => d.sales)} labels={analytics.aggregate.by_day.map((d) => d.date.slice(5))} />
        </div>
      )}

      {marketing.campaigns.length > 0 && (
        <PodContainer
          title="Top Campaigns"
          padding="lg"
          variant="default"
          style={{ marginTop: "1.5rem" }}
        >
          <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
            {marketing.campaigns.slice(0, 5).map((c) => (
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

