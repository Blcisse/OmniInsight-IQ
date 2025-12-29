import { proxyGet } from "../../_proxy";

export async function GET(
  req: Request,
  { params }: { params: { productId: string } }
) {
  const productId = params.productId;
  return proxyGet(`/api/forecasting/products/${productId}`, req);
}
