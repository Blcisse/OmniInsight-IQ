"use client";

import Link from "next/link";
import React, { useEffect, useMemo, useState } from "react";

import { getAnomalies, getEngagementSeries, getKpiSeries } from "@/app/lib/insightops/client";
import { Anomaly, SeriesPoint } from "@/app/lib/insightops/types";

type TrendMeta = {
  direction: "up" | "down" | "flat";
  percentChange: number | null;
  absoluteChange: number | null;
};

const metricOptions = [
  { value: "revenue", label: "Revenue" },
  { value: "pipeline", label: "Pipeline" },
  { value: "win_rate", label: "Win Rate" },
];

const signalOptions = [
  { value: "touches", label: "Touches" },
  { value: "replies", label: "Replies" },
  { value: "meetings", label: "Meetings" },
];

const formatNumber = (value: number | null | undefined, options?: Intl.NumberFormatOptions) => {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return value.toLocaleString(undefined, options);
};

const computeTrend = (series: SeriesPoint[]): TrendMeta => {
  const points = series
    .filter((point) => point.value !== null && point.value !== undefined)
    .map((point) => ({ ...point, value: Number(point.value) }));

  if (points.length === 0) return { direction: "flat", percentChange: null, absoluteChange: null };

  const last = points[points.length - 1].value;
  const prev = points.length > 1 ? points[points.length - 2].value : null;

  if (prev === null || prev === 0) {
    return { direction: "flat", percentChange: null, absoluteChange: null };
  }

  const absoluteChange = last - prev;
  const percentChange = (absoluteChange / prev) * 100;
  const direction = percentChange > 0 ? "up" : percentChange < 0 ? "down" : "flat";

  return { direction, percentChange, absoluteChange };
};

const TrendBadge = ({ trend }: { trend: TrendMeta }) => {
  const { direction, percentChange } = trend;
  const color =
    direction === "up" ? "#16a34a" : direction === "down" ? "#dc2626" : "var(--text-secondary, #64748b)";
  const arrow = direction === "up" ? "▲" : direction === "down" ? "▼" : "■";

  return (
    <span style={{ color, fontWeight: 600, display: "inline-flex", alignItems: "center", gap: 6 }}>
      <span style={{ fontSize: 12 }}>{arrow}</span>
      {percentChange !== null ? `${percentChange.toFixed(1)}%` : "No recent movement"}
    </span>
  );
};

const Table = ({ title, series }: { title: string; series: SeriesPoint[] }) => {
  if (series.length === 0) {
    return (
      <div
        style={{
          border: "1px dashed var(--glass-border)",
          borderRadius: "var(--radius-lg)",
          padding: "1rem",
          color: "var(--text-secondary)",
        }}
      >
        No {title.toLowerCase()} available for this filter set.
      </div>
    );
  }

  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse", minWidth: 480 }}>
        <thead>
          <tr style={{ textAlign: "left", color: "var(--text-secondary)" }}>
            <th style={{ padding: "0.5rem", borderBottom: "1px solid var(--glass-border)" }}>Date</th>
            <th style={{ padding: "0.5rem", borderBottom: "1px solid var(--glass-border)" }}>Value</th>
            <th style={{ padding: "0.5rem", borderBottom: "1px solid var(--glass-border)" }}>Δ from previous</th>
          </tr>
        </thead>
        <tbody>
          {series.map((point, idx) => {
            const prev = idx > 0 ? series[idx - 1].value : null;
            const delta = point.value !== null && prev !== null ? point.value - prev : null;
            return (
              <tr key={`${point.date}-${idx}`} style={{ borderBottom: "1px solid var(--glass-border)" }}>
                <td style={{ padding: "0.5rem" }}>{point.date}</td>
                <td style={{ padding: "0.5rem" }}>{formatNumber(point.value)}</td>
                <td style={{ padding: "0.5rem", color: delta !== null ? (delta >= 0 ? "#16a34a" : "#dc2626") : "inherit" }}>
                  {delta === null ? "—" : `${delta >= 0 ? "+" : ""}${delta.toFixed(2)}`}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default function AnalystViewPage() {
  const [orgId, setOrgId] = useState("demo_org");
  const [metricKey, setMetricKey] = useState("revenue");
  const [signalKey, setSignalKey] = useState("touches");
  const [lookbackDays, setLookbackDays] = useState(14);

  const [kpiSeries, setKpiSeries] = useState<SeriesPoint[]>([]);
  const [engagementSeries, setEngagementSeries] = useState<SeriesPoint[]>([]);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function fetchData() {
      setLoading(true);
      setError(null);
      try {
        const [kpi, engagement, anomalyList] = await Promise.all([
          getKpiSeries({ orgId, metricKey, lookbackDays }),
          getEngagementSeries({ orgId, signalKey, lookbackDays }),
          getAnomalies({ orgId, metricKey, signalKey }),
        ]);
        if (cancelled) return;
        setKpiSeries(kpi ?? []);
        setEngagementSeries(engagement ?? []);
        setAnomalies(anomalyList ?? []);
      } catch (err: any) {
        if (cancelled) return;
        setError(err?.message || "Unable to load analyst view data.");
        setKpiSeries([]);
        setEngagementSeries([]);
        setAnomalies([]);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchData();
    return () => {
      cancelled = true;
    };
  }, [orgId, metricKey, signalKey, lookbackDays]);

  const kpiTrend = useMemo(() => computeTrend(kpiSeries), [kpiSeries]);
  const engagementTrend = useMemo(() => computeTrend(engagementSeries), [engagementSeries]);

  const latestKpi = useMemo(
    () => kpiSeries.filter((p) => p.value !== null && p.value !== undefined).slice(-1)[0]?.value ?? null,
    [kpiSeries]
  );
  const latestEngagement = useMemo(
    () => engagementSeries.filter((p) => p.value !== null && p.value !== undefined).slice(-1)[0]?.value ?? null,
    [engagementSeries]
  );

  return (
    <section style={{ display: "grid", gap: "1.5rem", maxWidth: 1200, margin: "0 auto", paddingBottom: "2rem" }}>
      <header style={{ display: "flex", justifyContent: "space-between", gap: "1rem", flexWrap: "wrap", alignItems: "center" }}>
        <div>
          <p style={{ color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 4 }}>
            Domain
          </p>
          <h1 className="heading-gradient" style={{ fontSize: "2rem", margin: 0 }}>
            InsightOps Analyst View
          </h1>
          <p style={{ color: "var(--text-secondary)", maxWidth: 680, marginTop: 8 }}>
            Deep-dive KPI and engagement telemetry with interactive filters. Select your org, window, KPI, and signal to
            validate anomalies and performance swings.
          </p>
        </div>
        <Link
          href="/insightops"
          style={{
            padding: "0.65rem 1rem",
            borderRadius: "var(--radius-lg)",
            border: "1px solid var(--glass-border)",
            background: "var(--glass-bg)",
            textDecoration: "none",
            color: "inherit",
          }}
        >
          ← Back to Executive View
        </Link>
      </header>

      <div className="glass-card" style={{ padding: "1rem", display: "grid", gap: "0.75rem" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "1rem", flexWrap: "wrap" }}>
          <h2 style={{ margin: 0 }}>Filters</h2>
          <div style={{ color: "var(--text-secondary)" }}>
            Currently viewing org <strong>{orgId}</strong> · Lookback <strong>{lookbackDays}d</strong> · KPI{" "}
            <strong>{metricKey}</strong> · Signal <strong>{signalKey}</strong>
          </div>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "0.75rem" }}>
          <label style={{ display: "grid", gap: 6, fontSize: 14 }}>
            Org ID
            <input
              value={orgId}
              onChange={(e) => setOrgId(e.target.value)}
              placeholder="demo_org"
              style={{ padding: "0.6rem", borderRadius: 10, border: "1px solid var(--glass-border)", background: "var(--glass-bg)" }}
            />
          </label>
          <label style={{ display: "grid", gap: 6, fontSize: 14 }}>
            Lookback (days)
            <input
              type="number"
              min={1}
              max={120}
              value={lookbackDays}
              onChange={(e) => setLookbackDays(Number(e.target.value) || 1)}
              style={{ padding: "0.6rem", borderRadius: 10, border: "1px solid var(--glass-border)", background: "var(--glass-bg)" }}
            />
          </label>
          <label style={{ display: "grid", gap: 6, fontSize: 14 }}>
            KPI
            <select
              value={metricKey}
              onChange={(e) => setMetricKey(e.target.value)}
              style={{ padding: "0.6rem", borderRadius: 10, border: "1px solid var(--glass-border)", background: "var(--glass-bg)" }}
            >
              {metricOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
          <label style={{ display: "grid", gap: 6, fontSize: 14 }}>
            Signal
            <select
              value={signalKey}
              onChange={(e) => setSignalKey(e.target.value)}
              style={{ padding: "0.6rem", borderRadius: 10, border: "1px solid var(--glass-border)", background: "var(--glass-bg)" }}
            >
              {signalOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
        </div>
      </div>

      {loading && <div style={{ color: "var(--text-secondary)" }}>Loading analyst data…</div>}
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
        <>
          <div style={{ display: "grid", gap: "0.75rem", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))" }}>
            <div className="glass-card" style={{ padding: "1rem", display: "grid", gap: 6 }}>
              <div style={{ color: "var(--text-secondary)", fontSize: 14 }}>KPI ({metricKey})</div>
              <div style={{ fontSize: 26, fontWeight: 700 }}>{formatNumber(latestKpi)}</div>
              <TrendBadge trend={kpiTrend} />
            </div>
            <div className="glass-card" style={{ padding: "1rem", display: "grid", gap: 6 }}>
              <div style={{ color: "var(--text-secondary)", fontSize: 14 }}>Engagement ({signalKey})</div>
              <div style={{ fontSize: 26, fontWeight: 700 }}>{formatNumber(latestEngagement)}</div>
              <TrendBadge trend={engagementTrend} />
            </div>
            <div className="glass-card" style={{ padding: "1rem", display: "grid", gap: 6 }}>
              <div style={{ color: "var(--text-secondary)", fontSize: 14 }}>Anomalies</div>
              <div style={{ fontSize: 26, fontWeight: 700 }}>{anomalies.length}</div>
              <div style={{ color: "var(--text-secondary)" }}>
                {anomalies.length === 0 ? "No anomalies detected" : "Review detected anomalies below"}
              </div>
            </div>
          </div>

          <div className="glass-card" style={{ padding: "1rem", display: "grid", gap: "0.75rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "1rem" }}>
              <h3 style={{ margin: 0 }}>KPI Series</h3>
              <span style={{ color: "var(--text-secondary)" }}>Last {lookbackDays} days · {metricKey}</span>
            </div>
            <Table title="KPI series" series={kpiSeries} />
          </div>

          <div className="glass-card" style={{ padding: "1rem", display: "grid", gap: "0.75rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "1rem" }}>
              <h3 style={{ margin: 0 }}>Engagement Series</h3>
              <span style={{ color: "var(--text-secondary)" }}>Last {lookbackDays} days · {signalKey}</span>
            </div>
            <Table title="Engagement series" series={engagementSeries} />
          </div>

          <div className="glass-card" style={{ padding: "1rem", display: "grid", gap: "0.75rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "1rem" }}>
              <h3 style={{ margin: 0 }}>Anomalies</h3>
              <span style={{ color: "var(--text-secondary)" }}>Metric: {metricKey} · Signal: {signalKey}</span>
            </div>
            {anomalies.length === 0 ? (
              <div style={{ color: "var(--text-secondary)" }}>No anomalies for this selection.</div>
            ) : (
              <div style={{ display: "grid", gap: "0.5rem" }}>
                {anomalies.map((anomaly, idx) => (
                  <div
                    key={`${anomaly.type}-${idx}`}
                    style={{
                      border: "1px solid var(--glass-border)",
                      borderRadius: "var(--radius-lg)",
                      padding: "0.75rem",
                      display: "grid",
                      gap: 4,
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <strong>{anomaly.type}</strong>
                      <span
                        style={{
                          padding: "0.25rem 0.6rem",
                          borderRadius: 999,
                          fontSize: 12,
                          background:
                            anomaly.severity === "critical"
                              ? "rgba(248,113,113,0.14)"
                              : anomaly.severity === "warning"
                                ? "rgba(251,191,36,0.14)"
                                : "rgba(59,130,246,0.14)",
                          color:
                            anomaly.severity === "critical"
                              ? "#ef4444"
                              : anomaly.severity === "warning"
                                ? "#f59e0b"
                                : "#3b82f6",
                        }}
                      >
                        {anomaly.severity}
                      </span>
                    </div>
                    <div style={{ color: "var(--text-secondary)" }}>{anomaly.description}</div>
                    <div style={{ fontSize: 12, color: "var(--text-secondary)" }}>{anomaly.date}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </section>
  );
}
