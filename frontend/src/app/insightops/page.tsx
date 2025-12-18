"use client";

import React, { useEffect, useState } from "react";

type HealthResponse = {
  domain: string;
  status: string;
};

export default function InsightOpsPage() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function fetchHealth() {
      try {
        setLoading(true);
        const res = await fetch("/insightops/health");
        if (!res.ok) {
          throw new Error(`Request failed with status ${res.status}`);
        }
        const data = (await res.json()) as HealthResponse;
        if (isMounted) {
          setHealth(data);
          setError(null);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err?.message || "Unable to reach InsightOps health endpoint.");
          setHealth(null);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    fetchHealth();

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
          maxWidth: 520,
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
          <h2 style={{ margin: 0, fontSize: "1.1rem", color: "var(--text-primary)" }}>Health</h2>
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
            {loading ? "Checking" : health ? "OK" : "Issue"}
          </span>
        </div>
        {loading && <p style={{ margin: 0, color: "var(--text-secondary)" }}>Reaching /insightops/health…</p>}
        {!loading && error && (
          <p style={{ margin: 0, color: "#f87171" }}>
            {error}
          </p>
        )}
        {!loading && health && (
          <div style={{ display: "grid", gap: 4, color: "var(--text-secondary)" }}>
            <div>
              <span style={{ fontWeight: 600, color: "var(--text-primary)" }}>Domain:</span> {health.domain}
            </div>
            <div>
              <span style={{ fontWeight: 600, color: "var(--text-primary)" }}>Status:</span> {health.status}
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
