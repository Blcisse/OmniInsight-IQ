"use client";
import React, { useEffect, useState } from "react";
import MarketingTable from "@/app/components/tables/MarketingTable";
import MarketingROIGraph from "@/app/components/charts/MarketingROIGraph";

export default function MarketingPage() {
  const [rows, setRows] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const res = await fetch("/api/marketing/campaign-metrics");
        if (!res.ok) throw new Error("Failed to load marketing");
        setRows(await res.json());
        setError(null);
      } catch (e: any) {
        setError(e?.message || "Error loading marketing");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const roiData = rows.map((r: any) => ({ name: r.campaign_name, roi: r.roi }));

  return (
    <section>
      <h1>Marketing</h1>
      {loading && <p>Loading…</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {!loading && !error && (
        <>
          <div style={{ margin: "12px 0" }}>
            <MarketingROIGraph data={roiData} />
          </div>
          <MarketingTable rows={rows} />
        </>
      )}
    </section>
  );
}

