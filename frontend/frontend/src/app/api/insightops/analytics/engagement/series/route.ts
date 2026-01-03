import { proxyGet } from "../../../_proxy";

export async function GET(req: Request) {
  return proxyGet("/api/insightops/analytics/engagement/series", req);
}
