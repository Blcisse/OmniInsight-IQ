"use client";

import React, { useEffect, useState } from "react";

import ExecutiveDashboard from "./components/ExecutiveDashboard";
import { getAnomalies, getEngagementSummary, getKpiSummary } from "../lib/insightops/client";
import { Anomaly, EngagementSummaryResponse, KpiSummaryResponse } from "../lib/insightops/types";

type HealthResponse = {
  domain?: string;
  status?: string;
};

export default function InsightOpsPage() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [kpiSummaries, setKpiSummaries] = useState<{
    revenue?: KpiSummaryResponse | null;
    pipeline?: KpiSummaryResponse | null;
    win_rate?: KpiSummaryResponse | null;
  }>({});
  const [engagementSummary, setEngagementSummary] = useState<EngagementSummaryResponse | null>(null);
  const [anomalies, setAnomalies] = useState<Anomaly[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function fetchAll() {
      setLoading(true);
      try {
        const [healthRes, revenueRes, pipelineRes, winRateRes, engagementRes, anomaliesRes] = await Promise.all([
          fetch("/api/insightops/health").then((r) => {
            if (!r.ok) throw new Error(`Health failed ${r.status}`);
            return r.json() as Promise<HealthResponse>;
          }),
          getKpiSummary({ metricKey: "revenue" }),
          getKpiSummary({ metricKey: "pipeline" }),
          getKpiSummary({ metricKey: "win_rate" }),
          getEngagementSummary({ signalKey: "touches" }),
          getAnomalies({ metricKey: "revenue" }),
        ]);
        if (!isMounted) return;
        setHealth(healthRes);
        setKpiSummaries({
          revenue: revenueRes ?? null,
          pipeline: pipelineRes ?? null,
          win_rate: winRateRes ?? null,
        });
        setEngagementSummary(engagementRes ?? null);
        setAnomalies(anomaliesRes ?? null);
        setError(null);
      } catch (err: any) {
        if (!isMounted) return;
        setError(err?.message || "Unable to load InsightOps analytics.");
        setHealth(null);
        setKpiSummaries({});
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
    <section style={{ display: "grid", gap: "1.5rem", maxWidth: "1200px", margin: "0 auto", paddingBottom: "2rem" }}>
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

      {loading && <p style={{ margin: 0, color: "var(--text-secondary)" }}>Loading InsightOps data…</p>}
      {!loading && error && (
        <div
          style={{
            border: "1px solid var(--glass-border)",
            borderRadius: "var(--radius-lg)",
            padding: "1rem",
            background: "var(--glass-bg)",
            color: "#f87171",
          }}
        >
          {error}
        </div>
      )}

      {!loading && !error && (
        <ExecutiveDashboard
          health={health}
          kpiSummaries={kpiSummaries}
          engagementSummary={engagementSummary}
          anomalies={anomalies}
        />
      )}
    </section>
  );
}
