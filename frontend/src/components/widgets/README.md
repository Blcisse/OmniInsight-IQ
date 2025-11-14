# Live Analytics Visualization Widgets

This directory contains reusable widget components for live analytics visualization using Recharts.

## Widgets

### 1. LineChartWidget.tsx
- **Purpose**: Display trends and forecasts over time
- **Features**:
  - Multiple data series support
  - Interactive tooltips
  - Click handlers for drilldown
  - Customizable formatting
  - Responsive design

### 2. BarChartWidget.tsx
- **Purpose**: Display clustering and group comparisons
- **Features**:
  - Vertical and horizontal layouts
  - Multiple data series
  - Interactive tooltips
  - Click handlers
  - Customizable colors

### 3. KPIWidget.tsx
- **Purpose**: Display key performance indicators
- **Features**:
  - Multiple metrics in a grid
  - Delta/trend indicators
  - Click handlers
  - Responsive columns (1 on mobile, 2 on tablet, N on desktop)
  - Framer Motion animations

### 4. TableWidget.tsx
- **Purpose**: Display raw data in a sortable, paginated table
- **Features**:
  - Sortable columns
  - Pagination
  - Row click handlers
  - Custom cell formatting
  - Responsive horizontal scroll

## Example Components

See the `examples/` directory for complete implementations:
- `AnalyticsLineChartExample.tsx` - Sales trends
- `ForecastLineChartExample.tsx` - Forecast visualization
- `MarketingBarChartExample.tsx` - Campaign ROI comparison
- `AnalyticsKPIExample.tsx` - Analytics KPIs
- `MarketingTableExample.tsx` - Campaign data table

## Dynamic Updates

All widgets are connected to the Zustand store and automatically update when:
- Store state changes
- API calls complete
- Data is refreshed

The widgets subscribe to store state using hooks like `useAnalyticsStore()`, `useMarketingStore()`, etc., ensuring real-time updates when backend data changes.

## Usage

```tsx
import LineChartWidget from "@/components/widgets/LineChartWidget";
import { useAnalyticsStore } from "@/store/hooks";

function MyComponent() {
  const analytics = useAnalyticsStore();
  
  const chartData = analytics.aggregate?.by_day.map(point => ({
    date: point.date,
    sales: point.sales,
  })) || [];

  return (
    <LineChartWidget
      data={chartData}
      dataKeys={[{ key: "sales", name: "Sales", color: "#3b82f6" }]}
      title="Sales Trends"
      onDataPointClick={(data, index) => {
        // Handle drilldown
      }}
    />
  );
}
```

## Responsive Design

All widgets are responsive:
- **Mobile** (< 640px): Single column layouts, optimized spacing
- **Tablet** (640px - 1024px): 2-column layouts
- **Desktop** (> 1024px): Full multi-column layouts

The `WidgetContainer` component provides a responsive grid layout for multiple widgets.

