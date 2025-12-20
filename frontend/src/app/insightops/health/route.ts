import { proxyGet } from "../../api/insightops/_proxy";

export async function GET(request: Request) {
  return proxyGet("/insightops/health", request);
}

