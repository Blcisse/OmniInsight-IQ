"use client";
import React, { useEffect } from "react";
import { useMarketingStore } from "@/store/hooks";
import TableWidget, { TableColumn } from "../TableWidget";

type Campaign = {
  id: number;
  campaign_name?: string;
  name?: string;
  channel: string;
  budget: number;
  spend: number;
  impressions: number;
  clicks: number;
  ctr: number;
  cpc: number;
  roi?: number;
};

export default function MarketingTableExample() {
  const marketing = useMarketingStore();

  useEffect(() => {
    if (marketing.campaigns.length === 0 && !marketing.loading) {
      marketing.fetchCampaigns();
    }
  }, [marketing]);

  const columns: TableColumn<Campaign>[] = [
    {
      key: "id",
      label: "ID",
      sortable: true,
      width: 80,
    },
    {
      key: "campaign_name",
      label: "Campaign Name",
      sortable: true,
      format: (value, row) => row.campaign_name || row.name || `Campaign ${row.id}`,
    },
    {
      key: "channel",
      label: "Channel",
      sortable: true,
    },
    {
      key: "budget",
      label: "Budget",
      sortable: true,
      format: (value) => `$${Number(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      align: "right",
    },
    {
      key: "spend",
      label: "Spend",
      sortable: true,
      format: (value) => `$${Number(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      align: "right",
    },
    {
      key: "impressions",
      label: "Impressions",
      sortable: true,
      format: (value) => Number(value).toLocaleString(),
      align: "right",
    },
    {
      key: "clicks",
      label: "Clicks",
      sortable: true,
      format: (value) => Number(value).toLocaleString(),
      align: "right",
    },
    {
      key: "ctr",
      label: "CTR",
      sortable: true,
      format: (value) => `${(Number(value) * 100).toFixed(2)}%`,
      align: "right",
    },
    {
      key: "roi",
      label: "ROI",
      sortable: true,
      format: (value) => value ? `${Number(value).toFixed(2)}x` : "—",
      align: "right",
    },
  ];

  const handleRowClick = (row: Campaign, index: number) => {
    console.log("Clicked row:", row, "at index:", index);
    // Can navigate to campaign details
    marketing.setSelectedCampaign(row);
  };

  return (
    <TableWidget
      data={marketing.campaigns}
      columns={columns}
      title="Marketing Campaigns"
      pageSize={10}
      loading={marketing.loading}
      onRowClick={handleRowClick}
      emptyMessage="No campaigns available"
    />
  );
}

