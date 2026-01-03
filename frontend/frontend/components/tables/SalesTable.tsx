"use client";
import React, { useMemo, useState } from "react";

type Sale = {
  id: number;
  product_id: string;
  date: string;
  region?: string | null;
  units_sold: number;
  revenue: number;
  profit_margin?: number | null;
};

type Props = {
  rows: Sale[];
  pageSize?: number;
};

type SortKey = keyof Pick<Sale, "date" | "region" | "units_sold" | "revenue" | "profit_margin">;

export default function SalesTable({ rows, pageSize = 10 }: Props) {
  const [page, setPage] = useState(0);
  const [sortKey, setSortKey] = useState<SortKey>("date");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  const sorted = useMemo(() => {
    const copy = [...rows];
    copy.sort((a, b) => {
      const av = (a as any)[sortKey] ?? 0;
      const bv = (b as any)[sortKey] ?? 0;
      if (av < bv) return sortDir === "asc" ? -1 : 1;
      if (av > bv) return sortDir === "asc" ? 1 : -1;
      return 0;
    });
    return copy;
  }, [rows, sortKey, sortDir]);

  const start = page * pageSize;
  const pageRows = sorted.slice(start, start + pageSize);
  const pageCount = Math.ceil(rows.length / pageSize);

  function onSort(key: SortKey) {
    if (key === sortKey) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else {
      setSortKey(key);
      setSortDir("asc");
    }
  }

  return (
    <div>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <Th onClick={() => onSort("date")} label="Date" active={sortKey === "date"} dir={sortDir} />
            <th style={th}>Product</th>
            <Th onClick={() => onSort("region")} label="Region" active={sortKey === "region"} dir={sortDir} />
            <Th onClick={() => onSort("units_sold")} label="Units" active={sortKey === "units_sold"} dir={sortDir} />
            <Th onClick={() => onSort("revenue")} label="Revenue" active={sortKey === "revenue"} dir={sortDir} />
            <Th onClick={() => onSort("profit_margin")} label="Margin" active={sortKey === "profit_margin"} dir={sortDir} />
          </tr>
        </thead>
        <tbody>
          {pageRows.map((r) => (
            <tr key={r.id}>
              <td style={td}>{r.date}</td>
              <td style={td}>{r.product_id}</td>
              <td style={td}>{r.region ?? "-"}</td>
              <td style={td}>{r.units_sold}</td>
              <td style={td}>${r.revenue.toFixed(2)}</td>
              <td style={td}>{r.profit_margin != null ? `${r.profit_margin.toFixed(2)}%` : "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <Pager page={page} pageCount={pageCount} onPage={setPage} />
    </div>
  );
}

function Th({ label, onClick, active, dir }: { label: string; onClick: () => void; active: boolean; dir: "asc" | "desc" }) {
  return (
    <th style={th} onClick={onClick}>
      <span style={{ cursor: "pointer", userSelect: "none" }}>
        {label} {active ? (dir === "asc" ? "▲" : "▼") : ""}
      </span>
    </th>
  );
}

function Pager({ page, pageCount, onPage }: { page: number; pageCount: number; onPage: (p: number) => void }) {
  return (
    <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", marginTop: 8 }}>
      <button disabled={page <= 0} onClick={() => onPage(0)}>First</button>
      <button disabled={page <= 0} onClick={() => onPage(page - 1)}>Prev</button>
      <span style={{ alignSelf: "center" }}>Page {page + 1} / {pageCount || 1}</span>
      <button disabled={page + 1 >= pageCount} onClick={() => onPage(page + 1)}>Next</button>
      <button disabled={page + 1 >= pageCount} onClick={() => onPage(pageCount - 1)}>Last</button>
    </div>
  );
}

const th: React.CSSProperties = { textAlign: "left", padding: 8, borderBottom: "1px solid #e2e8f0", color: "#475569", fontSize: 12 };
const td: React.CSSProperties = { padding: 8, borderBottom: "1px solid #f1f5f9", fontSize: 14 };

