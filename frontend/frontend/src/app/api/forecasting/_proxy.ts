const BACKEND_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export async function proxyGet(path: string, req: Request): Promise<Response> {
  try {
    const url = new URL(req.url);
    const backendUrl = `${BACKEND_BASE_URL}${path}${url.search ? url.search : ""}`;
    const backendRes = await fetch(backendUrl, { method: "GET" });
    const text = await backendRes.text();
    return new Response(text, {
      status: backendRes.status,
      headers: {
        "content-type": backendRes.headers.get("content-type") ?? "application/json",
      },
    });
  } catch (error) {
    return new Response(JSON.stringify({ detail: "Bad Gateway" }), {
      status: 502,
      headers: { "content-type": "application/json" },
    });
  }
}

export { BACKEND_BASE_URL };
