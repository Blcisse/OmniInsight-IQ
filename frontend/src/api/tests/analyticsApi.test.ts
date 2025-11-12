import { getAnalyticsSummary, getAnalyticsPredict } from "../analyticsApi";

(async () => {
  const s = await getAnalyticsSummary();
  if (!s.ok || typeof s.data !== "object") throw new Error("summary shape invalid");
  const p = await getAnalyticsPredict(3);
  if (!p.ok || !Array.isArray(p.data?.forecast ?? p.data)) {
    // Allow either {forecast:[...]} or [...] depending on backend
    throw new Error("predict shape invalid");
  }
  console.log("analyticsApi ok");
})().catch((e) => {
  console.error(e);
  process.exit(1);
});

