import { NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { searchParams } = new URL(req.url);
    const horizon = searchParams.get("horizon") || "30";

    const response = await fetch(
      `${BACKEND_URL}/api/forecasting/products/batch?horizon=${horizon}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      }
    );

    if (!response.ok) {
      throw new Error(`Backend responded with ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error: any) {
    console.error("Forecasting batch proxy error:", error);
    return NextResponse.json(
      { error: error.message || "Failed to fetch batch forecasts" },
      { status: 500 }
    );
  }
}
