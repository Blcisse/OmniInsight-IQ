"use client";
import React from "react";

type Props = {
  label: string;
  value: string | number;
  delta?: number; // percentage change, positive or negative
};

export default function KPICard({ label, value, delta }: Props) {
  const isPositive = typeof delta === "number" ? delta >= 0 : true;
  const color = typeof delta === "number" ? (isPositive ? "#16a34a" : "#dc2626") : "#64748b";

  return (
    <div className="glass-card" style={{ padding: 16 }}>
      <div className="metrics-grid__label" style={{ textTransform: "none", letterSpacing: 0 }}>{label}</div>
      <div style={{ fontSize: 22, fontWeight: 700, marginTop: 6 }}>{value}</div>
      {typeof delta === "number" && (
        <div style={{ marginTop: 6, fontSize: 12, color }}>
          {isPositive ? "▲" : "▼"} {Math.abs(delta).toFixed(2)}%
        </div>
      )}
    </div>
  );
}
