import { proxyGet } from "../../_proxy";

export async function GET(req: Request) {
  return proxyGet("/insightops/executive-summaries/latest", req);
}
