import { proxyGet } from "../../../../_proxy";

export async function GET(req: Request) {
  return proxyGet("/insightops/analytics/engagement/summary", req);
}
