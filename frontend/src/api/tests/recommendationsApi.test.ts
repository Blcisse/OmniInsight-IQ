import { getRecommendations } from "../recommendationsApi";

(async () => {
  const r = await getRecommendations(3);
  if (!r.ok) throw new Error("recommendations request failed: " + r.error);
  if (!Array.isArray(r.data)) throw new Error("recommendations should be an array");
  console.log("recommendationsApi ok");
})().catch((e) => {
  console.error(e);
  process.exit(1);
});

