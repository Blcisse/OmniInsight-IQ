import { proxyGet } from "../_proxy";

export async function GET(req: Request) {
  return proxyGet("/api/forecasting/metrics", req);
}
