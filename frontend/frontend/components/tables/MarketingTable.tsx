"use client";
import React, { useMemo, useState } from "react";

type Campaign = {
  id: number;
  campaign_name: string;
  channel: string;
  budget: number;
  spend: number;
  impressions: number;
  clicks: number;
  roi: number;
};

type Props = {
  rows: Campaign[];
  pageSize?: number;
};

type SortKey = keyof Pick<Campaign, "campaign_name" | "channel" | "budget" | "spend" | "impressions" | "clicks" | "roi">;

export default function MarketingTable({ rows, pageSize = 10 }: Props) {
  const [page, setPage] = useState(0);
  const [sortKey, setSortKey] = useState<SortKey>("roi");
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
            <th style={th}>ID</th>
            <Th onClick={() => onSort("campaign_name")} label="Campaign" active={sortKey === "campaign_name"} dir={sortDir} />
            <Th onClick={() => onSort("channel")} label="Channel" active={sortKey === "channel"} dir={sortDir} />
            <Th onClick={() => onSort("budget")} label="Budget" active={sortKey === "budget"} dir={sortDir} />
            <Th onClick={() => onSort("spend")} label="Spend" active={sortKey === "spend"} dir={sortDir} />
            <Th onClick={() => onSort("impressions")} label="Impressions" active={sortKey === "impressions"} dir={sortDir} />
            <Th onClick={() => onSort("clicks")} label="Clicks" active={sortKey === "clicks"} dir={sortDir} />
            <Th onClick={() => onSort("roi")} label="ROI" active={sortKey === "roi"} dir={sortDir} />
          </tr>
        </thead>
        <tbody>
          {pageRows.map((r) => (
            <tr key={r.id}>
              <td style={td}>{r.id}</td>
              <td style={td}>{r.campaign_name}</td>
              <td style={td}>{r.channel}</td>
              <td style={td}>${r.budget.toFixed(2)}</td>
              <td style={td}>${r.spend.toFixed(2)}</td>
              <td style={td}>{r.impressions.toLocaleString()}</td>
              <td style={td}>{r.clicks.toLocaleString()}</td>
              <td style={td}>{r.roi.toFixed(2)}x</td>
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

