"use client";

import React from "react";

import KPICard from "@/app/components/cards/KPICard";
import { formatDelta } from "@/app/lib/insightops/diagnostics";
import { Anomaly, EngagementSummaryResponse, KpiSummaryResponse } from "@/app/lib/insightops/types";

type Health = {
  domain?: string;
  status?: string;
};

type Props = {
  kpiSummary: KpiSummaryResponse | null;
  engagementSummary: EngagementSummaryResponse | null;
  anomalies: Anomaly[] | null;
  health: Health | null;
};

const labelForHealthScore = (score: number | null | undefined): string => {
  if (score === null || score === undefined) return "Unknown";
  if (score >= 70) return "Healthy";
  if (score >= 40) return "Watch";
  return "Critical";
};

const displayNumber = (value: number | null | undefined, options?: Intl.NumberFormatOptions) => {
  if (value === null || value === undefined) return "—";
  return value.toLocaleString(undefined, options);
};

export default function ExecutiveDashboard({ kpiSummary, engagementSummary, anomalies, health }: Props) {
  const kpiCards = [
    { label: "Revenue", value: kpiSummary?.latest_value },
    { label: "Pipeline", value: kpiSummary?.latest_value },
    { label: "Win Rate", value: kpiSummary?.latest_value },
  ];

  const deltaText = kpiSummary ? formatDelta(kpiSummary) : "—";
  const rolling = kpiSummary?.rolling_average_7d_latest ?? kpiSummary?.rolling_average_7d ?? null;

  const engagementHealthScore = engagementSummary?.health_score ?? 0;
  const engagementLabel = labelForHealthScore(engagementHealthScore);

  const anomalyList = anomalies ?? [];

  return (
    <div className="glass-card" style={{ padding: "1.25rem", display: "grid", gap: "1rem" }}>
      <div>
        <p style={{ color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 4 }}>
          Executive View
        </p>
        <h2 style={{ margin: 0 }}>InsightOps Executive Dashboard</h2>
        <p style={{ marginTop: 6, color: "var(--text-secondary)" }}>Board-ready operational intelligence (demo)</p>
      </div>

      <div
        style={{
          display: "flex",
          gap: "0.75rem",
          flexWrap: "wrap",
          alignItems: "center",
          border: "1px solid var(--glass-border)",
          borderRadius: "var(--radius-lg)",
          padding: "0.75rem 1rem",
          background: "var(--glass-bg)",
        }}
      >
        <span
          style={{
            padding: "0.35rem 0.75rem",
            borderRadius: "9999px",
            background: health?.status === "ok" ? "rgba(16, 185, 129, 0.14)" : "rgba(248, 113, 113, 0.16)",
            color: health?.status === "ok" ? "#10b981" : "#ef4444",
            fontWeight: 700,
            border: "1px solid var(--glass-border)",
          }}
        >
          {health?.status === "ok" ? "Connected" : "Disconnected"}
        </span>
        <span style={{ color: "var(--text-secondary)" }}>Domain: {health?.domain ?? "insightops-studio"}</span>
      </div>

      <div style={{ display: "grid", gap: "0.75rem" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "0.75rem" }}>
          {kpiCards.map((card) => (
            <KPICard
              key={card.label}
              label={card.label}
              value={displayNumber(card.value)}
              delta={kpiSummary?.percent_delta ?? undefined}
            />
          ))}
        </div>
        <div style={{ fontSize: 12, color: "var(--text-secondary)" }}>
          Delta: {deltaText} · Rolling 7d avg: {displayNumber(rolling)}
        </div>
      </div>

      <div
        style={{
          border: "1px solid var(--glass-border)",
          borderRadius: "var(--radius-lg)",
          padding: "1rem",
          background: "var(--glass-bg)",
        }}
      >
        <h3 style={{ marginTop: 0 }}>Engagement Health</h3>
        <div style={{ display: "flex", gap: "1.5rem", flexWrap: "wrap" }}>
          <div>
            <div style={{ color: "var(--text-secondary)" }}>Health Score</div>
            <div style={{ fontSize: 24, fontWeight: 700 }}>
              {displayNumber(engagementSummary?.health_score)} ({engagementLabel})
            </div>
          </div>
          <div>
            <div style={{ color: "var(--text-secondary)" }}>Average per Day</div>
            <div style={{ fontSize: 18, fontWeight: 700 }}>{displayNumber(engagementSummary?.average_per_day)}</div>
          </div>
          <div>
            <div style={{ color: "var(--text-secondary)" }}>Last Day</div>
            <div style={{ fontSize: 18, fontWeight: 700 }}>{displayNumber(engagementSummary?.last_day_value)}</div>
          </div>
        </div>
      </div>

      <div
        style={{
          border: "1px solid var(--glass-border)",
          borderRadius: "var(--radius-lg)",
          padding: "1rem",
          background: "var(--glass-bg)",
        }}
      >
        <h3 style={{ marginTop: 0 }}>Risks / Anomalies</h3>
        {anomalyList.length === 0 ? (
          <p style={{ color: "var(--text-secondary)", margin: 0 }}>No anomalies detected.</p>
        ) : (
          <div style={{ display: "grid", gap: "0.5rem" }}>
            {anomalyList.map((item, idx) => (
              <div
                key={`${item.type}-${idx}`}
                style={{
                  border: "1px solid var(--glass-border)",
                  borderRadius: 8,
                  padding: "0.75rem",
                  display: "grid",
                  gap: "0.25rem",
                }}
              >
                <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", justifyContent: "space-between" }}>
                  <strong>{item.type}</strong>
                  <span
                    style={{
                      padding: "0.25rem 0.5rem",
                      borderRadius: "9999px",
                      fontSize: 12,
                      background:
                        item.severity === "critical"
                          ? "rgba(248,113,113,0.16)"
                          : item.severity === "warning"
                            ? "rgba(251,191,36,0.16)"
                            : "rgba(59,130,246,0.16)",
                      color:
                        item.severity === "critical"
                          ? "#ef4444"
                          : item.severity === "warning"
                            ? "#f59e0b"
                            : "#3b82f6",
                    }}
                  >
                    {item.severity}
                  </span>
                </div>
                <div style={{ color: "var(--text-secondary)" }}>{item.description}</div>
                <div style={{ fontSize: 12, color: "var(--text-secondary)" }}>{item.date}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
