"use client";
import React from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

type Campaign = { name: string; roi: number };

export default function MarketingROIGraph({ data }: { data: Campaign[] }) {
  return (
    <div style={{ width: "100%", height: 280 }}>
      <ResponsiveContainer>
        <BarChart data={data} margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" tick={{ fontSize: 12 }} interval={0} angle={-20} height={60} textAnchor="end" />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip formatter={(v: any) => [`${Number(v).toFixed(2)}x`, "ROI"]} />
          <Bar dataKey="roi" fill="#22c55e" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

