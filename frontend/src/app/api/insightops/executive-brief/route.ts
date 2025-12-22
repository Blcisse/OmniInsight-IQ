import { proxyGet } from "../_proxy";

export async function GET(req: Request) {
  // Forward all query params (including demo_mode/demo_profile) to the backend executive brief endpoint.
  return proxyGet("/insightops/executive-brief", req);
}
