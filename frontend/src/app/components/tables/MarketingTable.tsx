"use client";
import React from "react";

type Row = {
  id: number;
  campaign_name?: string;
  name?: string;
  channel: string;
  spend: number;
  impressions: number;
  clicks: number;
  roi?: number;
};

type Props = {
  rows: Row[];
};

export default function MarketingTable({ rows }: Props) {
  return (
    <div className="glass-card" style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ textAlign: "left", borderBottom: "1px solid rgba(255,255,255,0.1)" }}>
            <th style={{ padding: "8px 12px" }}>Campaign</th>
            <th style={{ padding: "8px 12px" }}>Channel</th>
            <th style={{ padding: "8px 12px" }}>Spend</th>
            <th style={{ padding: "8px 12px" }}>Clicks</th>
            <th style={{ padding: "8px 12px" }}>Impressions</th>
            <th style={{ padding: "8px 12px" }}>ROI</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id} style={{ borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
              <td style={{ padding: "8px 12px" }}>{row.campaign_name || row.name || `Campaign ${row.id}`}</td>
              <td style={{ padding: "8px 12px" }}>{row.channel}</td>
              <td style={{ padding: "8px 12px" }}>${row.spend.toLocaleString()}</td>
              <td style={{ padding: "8px 12px" }}>{row.clicks.toLocaleString()}</td>
              <td style={{ padding: "8px 12px" }}>{row.impressions.toLocaleString()}</td>
              <td style={{ padding: "8px 12px" }}>{row.roi ? `${row.roi.toFixed(2)}x` : "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {rows.length === 0 && (
        <div style={{ padding: 16, textAlign: "center", color: "var(--text-tertiary)" }}>
          No campaigns to display.
        </div>
      )}
    </div>
  );
}

