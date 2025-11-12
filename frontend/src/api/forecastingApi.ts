import { http, toApiResponse, ApiResponse } from "./http";

export async function getProductForecast(
  productId: string,
  opts?: { start?: string; end?: string }
): Promise<ApiResponse<any>> {
  const params: any = { product_id: productId };
  if (opts?.start) params.start = opts.start;
  if (opts?.end) params.end = opts.end;
  return toApiResponse(http.get(`/health-intel/products/metrics`, { params }));
}
