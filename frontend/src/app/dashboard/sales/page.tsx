"use client";
import React, { useEffect, useState } from "react";
import SalesTable from "@/app/components/tables/SalesTable";

export default function SalesPage() {
  const [rows, setRows] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const res = await fetch("/api/sales");
        if (!res.ok) throw new Error("Failed to load sales");
        setRows(await res.json());
        setError(null);
      } catch (e: any) {
        setError(e?.message || "Error loading sales");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <section>
      <h1>Sales</h1>
      {loading && <p>Loading…</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {!loading && !error && <SalesTable rows={rows} />}
    </section>
  );
}

