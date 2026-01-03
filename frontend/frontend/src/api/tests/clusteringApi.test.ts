import { getCampaignClusters } from "../clusteringApi";

(async () => {
  const r = await getCampaignClusters(2);
  if (!r.ok) throw new Error("clusters request failed: " + r.error);
  if (!Array.isArray(r.data)) throw new Error("clusters should be an array");
  console.log("clusteringApi ok");
})().catch((e) => {
  console.error(e);
  process.exit(1);
});

