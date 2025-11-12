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
    <div style={{ border: "1px solid #e2e8f0", borderRadius: 8, padding: 16, background: "#fff" }}>
      <div style={{ color: "#64748b", fontSize: 12 }}>{label}</div>
      <div style={{ fontSize: 22, fontWeight: 700, marginTop: 6 }}>{value}</div>
      {typeof delta === "number" && (
        <div style={{ marginTop: 6, fontSize: 12, color }}>
          {isPositive ? "▲" : "▼"} {Math.abs(delta).toFixed(2)}%
        </div>
      )}
    </div>
  );
}

