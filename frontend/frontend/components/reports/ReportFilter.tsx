"use client";
import React from "react";

export type ReportFilterValue = {
  startDate?: string;
  endDate?: string;
  region?: string;
  q?: string;
};

type Props = {
  value: ReportFilterValue;
  onChange: (next: ReportFilterValue) => void;
};

export default function ReportFilter({ value, onChange }: Props) {
  function update<K extends keyof ReportFilterValue>(key: K, val: ReportFilterValue[K]) {
    onChange({ ...value, [key]: val });
  }

  return (
    <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
      <div>
        <label style={{ display: "block", fontSize: 12, color: "#64748b" }}>Start</label>
        <input type="date" value={value.startDate || ""} onChange={(e) => update("startDate", e.target.value)} />
      </div>
      <div>
        <label style={{ display: "block", fontSize: 12, color: "#64748b" }}>End</label>
        <input type="date" value={value.endDate || ""} onChange={(e) => update("endDate", e.target.value)} />
      </div>
      <div>
        <label style={{ display: "block", fontSize: 12, color: "#64748b" }}>Region</label>
        <input type="text" placeholder="e.g., NA" value={value.region || ""} onChange={(e) => update("region", e.target.value)} />
      </div>
      <div style={{ minWidth: 220 }}>
        <label style={{ display: "block", fontSize: 12, color: "#64748b" }}>Search</label>
        <input type="text" placeholder="keyword" value={value.q || ""} onChange={(e) => update("q", e.target.value)} />
      </div>
    </div>
  );
}

