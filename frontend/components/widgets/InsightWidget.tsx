"use client";
import React, { useEffect, useState } from "react";

type Insight = {
  title: string;
  category: string;
  recommendation: string;
  impact?: string;
  confidence?: number;
};

export default function InsightWidget() {
  const [insights, setInsights] = useState<Insight[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const res = await fetch("/api/insights/aggregate");
        if (!res.ok) throw new Error("Failed to load insights");
        const json = await res.json();
        const fromEngine = (json?.clusters || []).slice(0, 3).map((c: any, i: number) => ({
          title: `Cluster ${c.cluster}: ${c.size} items`,
          category: "analytics",
          recommendation: `Focus on members: ${c.members?.slice(0, 5).join(", ") || "n/a"}`,
          impact: "medium",
          confidence: 0.7,
        }));
        setInsights(fromEngine);
        setError(null);
      } catch (e: any) {
        setError(e?.message || "Error loading insights");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <div>Loading insights…</div>;
  if (error) return <div style={{ color: "red" }}>{error}</div>;

  return (
    <div style={{ border: "1px solid #e2e8f0", borderRadius: 8, padding: 16 }}>
      <div style={{ fontWeight: 600, marginBottom: 8 }}>AI Recommendations</div>
      <ul style={{ margin: 0, padding: 0, listStyle: "none" }}>
        {insights.map((i, idx) => (
          <li key={idx} style={{ padding: "8px 0", borderBottom: idx + 1 < insights.length ? "1px solid #f1f5f9" : undefined }}>
            <div style={{ fontWeight: 600 }}>{i.title}</div>
            <div style={{ color: "#64748b", fontSize: 12 }}>{i.category} · {i.impact}</div>
            <div style={{ marginTop: 4 }}>{i.recommendation}</div>
            {i.confidence != null && (
              <div style={{ marginTop: 4, fontSize: 12, color: "#64748b" }}>Confidence: {(i.confidence * 100).toFixed(0)}%</div>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

