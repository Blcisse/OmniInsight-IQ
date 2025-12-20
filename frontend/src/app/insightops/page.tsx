"use client";

import React, { useEffect, useState } from "react";

import { getAnomalies, getEngagementSummary, getKpiSummary } from "../lib/insightops/client";
import { Anomaly, EngagementSummaryResponse, KpiSummaryResponse } from "../lib/insightops/types";

type HealthResponse = {
  domain: string;
  status: string;
};

export default function InsightOpsPage() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [kpiSummary, setKpiSummary] = useState<KpiSummaryResponse | null>(null);
  const [engagementSummary, setEngagementSummary] = useState<EngagementSummaryResponse | null>(null);
  const [anomalies, setAnomalies] = useState<Anomaly[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function fetchAll() {
        setLoading(true);
        try {
          const [healthRes, kpiRes, engagementRes, anomaliesRes] = await Promise.all([
            fetch("/insightops/health").then((r) => {
              if (!r.ok) throw new Error(`Health failed ${r.status}`);
              return r.json() as Promise<HealthResponse>;
            }),
            getKpiSummary(),
            getEngagementSummary(),
            getAnomalies({ metricKey: "revenue" }),
          ]);
          if (!isMounted) return;
          setHealth(healthRes);
          setKpiSummary(kpiRes);
          setEngagementSummary(engagementRes);
          setAnomalies(anomaliesRes);
          setError(null);
        } catch (err: any) {
          if (!isMounted) return;
          setError(err?.message || "Unable to load InsightOps analytics.");
          setHealth(null);
          setKpiSummary(null);
          setEngagementSummary(null);
          setAnomalies(null);
        } finally {
          if (isMounted) setLoading(false);
        }
    }

    fetchAll();

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <section style={{ display: "grid", gap: "1rem" }}>
      <header>
        <p style={{ color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 4 }}>
          Domain
        </p>
        <h1 className="heading-gradient" style={{ fontSize: "2rem", margin: 0 }}>
          InsightOps Studio
        </h1>
        <p style={{ color: "var(--text-secondary)", maxWidth: 640, marginTop: 8 }}>
          Commercial performance and engagement intelligence, scoped as a first-class domain within OmniInsight IQ.
        </p>
      </header>

      <div
        style={{
          border: "1px solid var(--glass-border)",
          borderRadius: "var(--radius-lg)",
          padding: "1rem 1.25rem",
          background: "var(--glass-bg)",
          boxShadow: "var(--shadow-glow)",
          maxWidth: 720,
          display: "grid",
          gap: "0.75rem",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
          <h2 style={{ margin: 0, fontSize: "1.1rem", color: "var(--text-primary)" }}>Diagnostics</h2>
          <span
            style={{
              padding: "0.3rem 0.65rem",
              borderRadius: "9999px",
              background: loading
                ? "var(--glass-border)"
                : health
                  ? "rgba(16, 185, 129, 0.14)"
                  : "rgba(248, 113, 113, 0.16)",
              color: loading ? "var(--text-secondary)" : health ? "#10b981" : "#ef4444",
              fontWeight: 600,
              border: "1px solid var(--glass-border)",
              fontSize: 12,
            }}
          >
            {loading ? "Loading" : health ? "Connected" : "Issue"}
          </span>
        </div>

        {loading && <p style={{ margin: 0, color: "var(--text-secondary)" }}>Loading InsightOps data…</p>}
        {!loading && error && (
          <p style={{ margin: 0, color: "#f87171" }}>
            {error}
          </p>
        )}

        {!loading && !error && (
          <div style={{ display: "grid", gap: "0.5rem" }}>
            <div>
              <div style={{ fontWeight: 600, color: "var(--text-primary)" }}>Health</div>
              <pre style={{ margin: 0, whiteSpace: "pre-wrap" }}>{JSON.stringify(health, null, 2)}</pre>
            </div>
            <div>
              <div style={{ fontWeight: 600, color: "var(--text-primary)" }}>KPI Summary (revenue)</div>
              <pre style={{ margin: 0, whiteSpace: "pre-wrap" }}>{JSON.stringify(kpiSummary, null, 2)}</pre>
            </div>
            <div>
              <div style={{ fontWeight: 600, color: "var(--text-primary)" }}>Engagement Summary (touches)</div>
              <pre style={{ margin: 0, whiteSpace: "pre-wrap" }}>{JSON.stringify(engagementSummary, null, 2)}</pre>
            </div>
            <div>
              <div style={{ fontWeight: 600, color: "var(--text-primary)" }}>Anomalies (revenue)</div>
              <pre style={{ margin: 0, whiteSpace: "pre-wrap" }}>{JSON.stringify(anomalies, null, 2)}</pre>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
