"use client";
import React, { useState } from "react";

type Props = {
  fmt?: "csv" | "pdf";
  startDate?: string;
  endDate?: string;
  label?: string;
};

export default function ExportReportButton({ fmt = "csv", startDate, endDate, label = "Export Report" }: Props) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onClick() {
    try {
      setLoading(true);
      setError(null);
      const params = new URLSearchParams();
      params.set("fmt", fmt);
      if (startDate) params.set("start_date", startDate);
      if (endDate) params.set("end_date", endDate);

      const res = await fetch(`/api/reports/generate?${params.toString()}`);
      if (!res.ok) {
        const txt = await res.text();
        throw new Error(txt || `Request failed: ${res.status}`);
      }
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      const ts = new Date().toISOString().replace(/[:.]/g, "");
      const ext = fmt === "pdf" ? "pdf" : "csv";
      a.href = url;
      a.download = `report_${ts}.${ext}`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (e: any) {
      setError(e?.message || "Download failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
      <button onClick={onClick} disabled={loading}>
        {loading ? "Preparing…" : label}
      </button>
      {error && <span style={{ color: "#dc2626", fontSize: 12 }}>{error}</span>}
    </div>
  );
}

