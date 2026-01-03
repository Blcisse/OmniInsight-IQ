"use client";
import React from "react";

type Props = {
  title: string;
  metrics: { label: string; value: string | number; delta?: number }[];
};

export default function AnalyticsSummaryCard({ title, metrics }: Props) {
  return (
    <div style={{ border: "1px solid #e2e8f0", borderRadius: 8, padding: 16, background: "#fff" }}>
      <div style={{ fontSize: 16, fontWeight: 600, marginBottom: 8 }}>{title}</div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 12 }}>
        {metrics.map((m) => (
          <Metric key={m.label} label={m.label} value={m.value} delta={m.delta} />)
        )}
      </div>
    </div>
  );
}

function Metric({ label, value, delta }: { label: string; value: string | number; delta?: number }) {
  const isPositive = typeof delta === "number" ? delta >= 0 : true;
  const color = typeof delta === "number" ? (isPositive ? "#16a34a" : "#dc2626") : "#64748b";

  return (
    <div>
      <div style={{ color: "#64748b", fontSize: 12 }}>{label}</div>
      <div style={{ fontSize: 18, fontWeight: 700 }}>{value}</div>
      {typeof delta === "number" && (
        <div style={{ marginTop: 4, fontSize: 12, color }}>
          {isPositive ? "▲" : "▼"} {Math.abs(delta).toFixed(2)}%
        </div>
      )}
    </div>
  );
}

