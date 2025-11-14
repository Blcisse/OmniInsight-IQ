"use client";
import React, { useEffect, useState } from "react";
import MarketingTable from "@/app/components/tables/MarketingTable";
import MarketingROIGraph from "@/app/components/charts/MarketingROIGraph";
import { useCampaigns, useConversions } from "@/lib/useMarketing";
import LoadingState from "@/components/LoadingState";
import ErrorDisplay from "@/components/ErrorDisplay";
import RetryButton from "@/components/RetryButton";
import CollapsiblePod from "@/ui/CollapsiblePod";
import Tabs from "@/ui/Tabs";

export default function MarketingPage() {
  const { data: campaigns, loading: cLoading, error: cErr, refresh: refreshC } = useCampaigns();
  const { data: conversions, loading: vLoading, error: vErr, refresh: refreshV } = useConversions();
  const [activeTab, setActiveTab] = useState<"roi" | "table">("roi");

  const loading = cLoading || vLoading;
  const error = cErr?.message || vErr?.message || null;

  const handleRetry = () => {
    refreshC();
    refreshV();
  };

  const roiData = campaigns.map((r) => ({
    name: r.campaign_name || r.name || `Campaign ${r.id}`,
    roi: r.roi || 0,
  }));

  return (
    <section>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <h1 className="heading-gradient">Marketing</h1>
        <RetryButton
          onRetry={handleRetry}
          label="Refresh"
          variant="outline"
          disabled={loading}
        />
      </div>

      <ErrorDisplay
        error={error}
        onRetry={handleRetry}
        variant="card"
        dismissible={true}
        onDismiss={() => {}}
      />

      <LoadingState loading={loading} error={error} message="Loading marketing data...">
        {!loading && !error && (
          <>
            <div className="flex items-center justify-between mt-3">
              <Tabs
                tabs={[{ id: "roi", label: "ROI" }, { id: "table", label: "Campaigns" }]}
                activeId={activeTab}
                onChange={(id) => setActiveTab(id as "roi" | "table")}
              />
            </div>
            <div className="grid grid-cols-12 gap-4 md:gap-6 mt-4">
              <div className="col-span-12 xl:col-span-7">
                <CollapsiblePod title="Campaign ROI" defaultOpen={activeTab === "roi"}>
                  <MarketingROIGraph data={roiData} />
                </CollapsiblePod>
              </div>
              <div className="col-span-12 xl:col-span-5">
                <CollapsiblePod title="Conversions" defaultOpen={conversions.length > 0}>
                  <div style={{ color: "var(--text-secondary)" }}>
                    {conversions.length ? `Showing ${conversions.length} conversion records.` : "No conversion data."}
                  </div>
                </CollapsiblePod>
              </div>
            </div>

            <div className="mt-6">
              <CollapsiblePod title="Campaign Table" defaultOpen={activeTab === "table"}>
                <MarketingTable rows={campaigns} />
              </CollapsiblePod>
            </div>
          </>
        )}
      </LoadingState>
    </section>
  );
}
