"use client";
import React, { useEffect, useState } from "react";
import { getFoodData, getFoodAnalyticsSummary, getFoodStats } from "@/api/processedDataApi";
import type { FoodItem, FoodAnalyticsSummary, FoodStats } from "@/api/processedDataApi";
import KPIWidget from "@/components/widgets/KPIWidget";
import TableWidget, { TableColumn } from "@/components/widgets/TableWidget";
import BarChartWidget, { BarChartDataPoint } from "@/components/widgets/BarChartWidget";

export default function DataTestPage() {
  const [foodData, setFoodData] = useState<FoodItem[]>([]);
  const [summary, setSummary] = useState<FoodAnalyticsSummary | null>(null);
  const [stats, setStats] = useState<FoodStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedGroup, setSelectedGroup] = useState<string>("");

  useEffect(() => {
    loadData();
  }, [selectedGroup]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [foodRes, summaryRes, statsRes] = await Promise.all([
        getFoodData(selectedGroup || undefined, 100, 0),
        getFoodAnalyticsSummary(),
        getFoodStats(),
      ]);

      if (!foodRes.ok) throw new Error(foodRes.error || "Failed to load food data");
      if (!summaryRes.ok) throw new Error(summaryRes.error || "Failed to load summary");
      if (!statsRes.ok) throw new Error(statsRes.error || "Failed to load stats");

      setFoodData(foodRes.data || []);
      setSummary(summaryRes.data || null);
      setStats(statsRes.data || null);
    } catch (e: any) {
      setError(e?.message || "Error loading data");
    } finally {
      setLoading(false);
    }
  };

  const tableColumns: TableColumn<FoodItem>[] = [
    { key: "food_name", label: "Food Name", sortable: true },
    { key: "calories", label: "Calories", sortable: true, format: (v) => v ? `${Number(v).toFixed(0)}` : "—" },
    { key: "protein", label: "Protein (g)", sortable: true, format: (v) => v ? `${Number(v).toFixed(1)}` : "—" },
    { key: "fat", label: "Fat (g)", sortable: true, format: (v) => v ? `${Number(v).toFixed(1)}` : "—" },
    { key: "carbohydrates", label: "Carbs (g)", sortable: true, format: (v) => v ? `${Number(v).toFixed(1)}` : "—" },
    { key: "data_group", label: "Group", sortable: true },
  ];

  const groupDistributionData: BarChartDataPoint[] = stats
    ? Object.entries(stats.by_group).map(([group, count]) => ({
        name: group,
        count,
      }))
    : [];

  if (loading) {
    return <div>Loading processed data...</div>;
  }

  if (error) {
    return <div style={{ color: "red" }}>Error: {error}</div>;
  }

  return (
    <section>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <h1>Processed Data Test Dashboard</h1>
        <div>
          <label style={{ marginRight: 8 }}>Filter by Group:</label>
          <select
            value={selectedGroup}
            onChange={(e) => setSelectedGroup(e.target.value)}
            style={{ padding: "6px 12px", borderRadius: 4, border: "1px solid #e2e8f0" }}
          >
            <option value="">All Groups</option>
            <option value="group1">Group 1</option>
            <option value="group2">Group 2</option>
            <option value="group3">Group 3</option>
            <option value="group4">Group 4</option>
            <option value="group5">Group 5</option>
          </select>
          <button
            onClick={loadData}
            style={{
              marginLeft: 8,
              padding: "6px 12px",
              borderRadius: 4,
              border: "1px solid #e2e8f0",
              background: "#3b82f6",
              color: "#fff",
              cursor: "pointer",
            }}
          >
            Refresh
          </button>
        </div>
      </div>

      {summary && (
        <div style={{ marginBottom: 24 }}>
          <KPIWidget
            metrics={[
              {
                label: "Total Foods",
                value: summary.total_foods,
                unit: undefined,
              },
              {
                label: "Avg Calories",
                value: summary.avg_calories,
                unit: undefined,
                formatValue: (v) => `${Number(v).toFixed(0)} cal`,
              },
              {
                label: "Avg Protein",
                value: summary.avg_protein,
                unit: undefined,
                formatValue: (v) => `${Number(v).toFixed(1)}g`,
              },
              {
                label: "Avg Fat",
                value: summary.avg_fat,
                unit: undefined,
                formatValue: (v) => `${Number(v).toFixed(1)}g`,
              },
            ]}
            title="Food Data Summary"
            columns={4}
          />
        </div>
      )}

      {groupDistributionData.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          <BarChartWidget
            data={groupDistributionData}
            dataKeys={[{ key: "count", name: "Food Items", color: "#3b82f6" }]}
            title="Food Items by Group"
            xAxisKey="name"
            yAxisLabel="Count"
            height={250}
          />
        </div>
      )}

      <div style={{ marginBottom: 24 }}>
        <TableWidget
          data={foodData}
          columns={tableColumns}
          title={`Food Items${selectedGroup ? ` - ${selectedGroup}` : ""}`}
          pageSize={20}
          loading={loading}
          emptyMessage="No food data available"
        />
      </div>
    </section>
  );
}

