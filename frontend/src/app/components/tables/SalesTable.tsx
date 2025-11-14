"use client";
import React from "react";

type SaleRow = {
  id: number;
  product_id: string;
  date: string;
  region?: string | null;
  units_sold: number;
  revenue: number;
};

type Props = {
  rows: SaleRow[];
};

export default function SalesTable({ rows }: Props) {
  return (
    <div className="glass-card" style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ textAlign: "left", borderBottom: "1px solid rgba(255,255,255,0.1)" }}>
            <th style={{ padding: "8px 12px" }}>Product</th>
            <th style={{ padding: "8px 12px" }}>Date</th>
            <th style={{ padding: "8px 12px" }}>Region</th>
            <th style={{ padding: "8px 12px" }}>Units Sold</th>
            <th style={{ padding: "8px 12px" }}>Revenue</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id} style={{ borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
              <td style={{ padding: "8px 12px" }}>{row.product_id}</td>
              <td style={{ padding: "8px 12px" }}>{row.date}</td>
              <td style={{ padding: "8px 12px" }}>{row.region || "-"}</td>
              <td style={{ padding: "8px 12px" }}>{row.units_sold}</td>
              <td style={{ padding: "8px 12px" }}>${row.revenue.toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {rows.length === 0 && (
        <div style={{ padding: 16, textAlign: "center", color: "var(--text-tertiary)" }}>No sales data available.</div>
      )}
    </div>
  );
}

