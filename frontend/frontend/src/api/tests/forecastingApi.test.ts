import { getProductForecast } from "../forecastingApi";

(async () => {
  const r = await getProductForecast("p1", { start: "2025-11-01", end: "2025-11-07" });
  if (!r.ok) throw new Error("forecast request failed: " + r.error);
  const ts = r.data?.timeseries;
  if (!Array.isArray(ts)) throw new Error("timeseries missing");
  console.log("forecastingApi ok");
})().catch((e) => {
  console.error(e);
  process.exit(1);
});

