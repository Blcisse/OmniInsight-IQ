"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { getExecutiveBrief } from "../../lib/insightops/client";
import { ExecutiveBriefResponse } from "../../lib/insightops/types";

export default function ExecutiveBriefPage() {
  const [brief, setBrief] = useState<ExecutiveBriefResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [demoMode, setDemoMode] = useState<boolean>(false);
  const [demoProfile, setDemoProfile] = useState<string>("EXEC_REVENUE_RISK");

  useEffect(() => {
    let mounted = true;

    async function loadBrief() {
      setLoading(true);
      try {
        const data = await getExecutiveBrief({
          orgId: "demo_org",
          windowDays: 14,
          demoMode,
          demoProfile: demoMode ? demoProfile : null,
        });
        if (!mounted) return;
        setBrief(data);
        setError(null);
      } catch (err: any) {
        if (!mounted) return;
        setError(err?.message || "Unable to load executive brief.");
        setBrief(null);
      } finally {
        if (mounted) setLoading(false);
      }
    }

    loadBrief();
    return () => {
      mounted = false;
    };
  }, [demoMode, demoProfile]);

  return (
    <section style={{ display: "grid", gap: "1.25rem", maxWidth: "960px", margin: "0 auto", paddingBottom: "2rem" }}>
      <header>
        <p style={{ color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 4 }}>
          InsightOps
        </p>
        <h1 style={{ fontSize: "2rem", margin: 0 }}>Executive Brief</h1>
        <p style={{ color: "var(--text-secondary)", marginTop: 6 }}>
          Deterministic board-ready summary composed from InsightOps analytics. Data shown for demo_org, 14-day window.
        </p>
        <Link href="/insightops" style={{ color: "var(--primary)", fontWeight: 500, marginTop: 8, display: "inline-block" }}>
          ← Back to Executive Dashboard
        </Link>
      </header>

      <div style={{ display: "flex", gap: "1rem", alignItems: "center", flexWrap: "wrap" }}>
        <label style={{ display: "flex", alignItems: "center", gap: "0.35rem" }}>
          <input
            type="checkbox"
            checked={demoMode}
            onChange={(e) => setDemoMode(e.target.checked)}
          />
          Demo Mode
        </label>
        <label style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <span style={{ color: "var(--text-secondary)" }}>Demo Profile</span>
          <select
            value={demoProfile}
            onChange={(e) => setDemoProfile(e.target.value)}
            disabled={!demoMode}
            style={{ padding: "0.25rem 0.5rem" }}
          >
            <option value="EXEC_REVENUE_RISK">EXEC_REVENUE_RISK</option>
            <option value="EXEC_ANOMALY_SPIKE">EXEC_ANOMALY_SPIKE</option>
            <option value="EXEC_STABLE_GROWTH">EXEC_STABLE_GROWTH</option>
            <option value="EXEC_ENGAGEMENT_DROP">EXEC_ENGAGEMENT_DROP</option>
          </select>
        </label>
      </div>

      {loading && <p style={{ color: "var(--text-secondary)" }}>Loading executive brief…</p>}
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

      {!loading && !error && brief && (
        <div
          style={{
            border: "1px solid var(--glass-border)",
            borderRadius: "var(--radius-lg)",
            padding: "1rem",
            background: "var(--glass-bg)",
            display: "grid",
            gap: "1rem",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: "0.75rem" }}>
            <div>
              <p style={{ margin: 0, color: "var(--text-secondary)" }}>Priority</p>
              <h2 style={{ margin: 0 }}>
                {brief.priority_score} / 100 <span style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>({brief.priority_level})</span>
              </h2>
            </div>
            <div style={{ textAlign: "right" }}>
              <p style={{ margin: 0, color: "var(--text-secondary)" }}>Window</p>
              <strong>{brief.window_days}-day</strong>
              <p style={{ margin: 0, color: "var(--text-secondary)", fontSize: "0.9rem" }}>
                Generated at {new Date(brief.generated_at).toLocaleString()}
              </p>
            </div>
          </div>

          <section>
            <h3 style={{ marginBottom: 6 }}>Insights</h3>
            {brief.insights.length === 0 ? (
              <p style={{ color: "var(--text-secondary)", margin: 0 }}>No insights captured.</p>
            ) : (
              <ul style={{ margin: 0, paddingLeft: "1.2rem", display: "grid", gap: "0.25rem" }}>
                {brief.insights.map((insight) => (
                  <li key={insight.title}>
                    <strong>{insight.title}:</strong> {insight.summary}
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section>
            <h3 style={{ marginBottom: 6 }}>Risks</h3>
            {brief.risks.length === 0 ? (
              <p style={{ color: "var(--text-secondary)", margin: 0 }}>No risks identified.</p>
            ) : (
              <ul style={{ margin: 0, paddingLeft: "1.2rem", display: "grid", gap: "0.25rem" }}>
                {brief.risks.map((risk) => (
                  <li key={risk.title}>
                    <strong>{risk.title}:</strong> {risk.description} (severity {risk.severity})
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section>
            <h3 style={{ marginBottom: 6 }}>Opportunities</h3>
            {brief.opportunities.length === 0 ? (
              <p style={{ color: "var(--text-secondary)", margin: 0 }}>No opportunities identified.</p>
            ) : (
              <ul style={{ margin: 0, paddingLeft: "1.2rem", display: "grid", gap: "0.25rem" }}>
                {brief.opportunities.map((opp) => (
                  <li key={opp.title}>
                    <strong>{opp.title}:</strong> {opp.description} (confidence {opp.confidence}%)
                  </li>
                ))}
              </ul>
            )}
          </section>

          {brief.notes?.length ? (
            <section>
              <h4 style={{ marginBottom: 6 }}>Notes</h4>
              <ul style={{ margin: 0, paddingLeft: "1.2rem", display: "grid", gap: "0.25rem" }}>
                {brief.notes.map((note, idx) => (
                  <li key={idx} style={{ color: "var(--text-secondary)" }}>
                    {note}
                  </li>
                ))}
              </ul>
            </section>
          ) : null}
        </div>
      )}
    </section>
  );
}
