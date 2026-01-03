"use client";
import React from "react";

type Column = { key: string; label: string };

type Props = {
  title: string;
  columns: Column[];
  rows: Record<string, any>[];
};

function toCSV(columns: Column[], rows: Record<string, any>[]) {
  const header = columns.map((c) => JSON.stringify(c.label)).join(",");
  const lines = rows.map((r) => columns.map((c) => JSON.stringify(r[c.key] ?? "")).join(","));
  return [header, ...lines].join("\n");
}

export default function ReportBuilder({ title, columns, rows }: Props) {
  function exportCSV() {
    const csv = toCSV(columns, rows);
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${title.replace(/\s+/g, "_").toLowerCase()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  async function exportPDF() {
    try {
      const { jsPDF } = await import("jspdf");
      const doc = new jsPDF();
      doc.text(title, 10, 10);
      let y = 20;
      const preview = rows.slice(0, 10);
      preview.forEach((row) => {
        const line = columns.map((c) => String(row[c.key] ?? "")).join(" | ");
        doc.text(line, 10, y);
        y += 8;
      });
      doc.save(`${title.replace(/\s+/g, "_").toLowerCase()}.pdf`);
    } catch (e) {
      alert("PDF export requires jspdf. Please install it in the project.");
    }
  }

  return (
    <div style={{ border: "1px solid #e2e8f0", borderRadius: 8, padding: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <strong>{title}</strong>
        <div style={{ display: "flex", gap: 8 }}>
          <button onClick={exportCSV}>Export CSV</button>
          <button onClick={exportPDF}>Export PDF</button>
        </div>
      </div>
    </div>
  );
}

