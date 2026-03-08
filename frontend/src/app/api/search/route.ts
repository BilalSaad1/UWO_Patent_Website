import { NextResponse } from "next/server";

const BACKEND_BASE =
  process.env.BACKEND_URL?.replace(/\/+$/, "") || "http://127.0.0.1:8000";

export async function GET(req: Request) {
  try {
    const url = new URL(req.url);
    const qs = url.searchParams.toString();
    const upstream = `${BACKEND_BASE}/search?${qs}`;

    const r = await fetch(upstream, {
      headers: { Accept: "application/json" },
      cache: "no-store",
    });

    const body = await r.text();

    return new NextResponse(body, {
      status: r.status,
      headers: {
        "Content-Type": r.headers.get("content-type") || "application/json",
      },
    });
  } catch (e) {
    console.error("Proxy /api/search failed:", e);
    return NextResponse.json({ error: "proxy_failed" }, { status: 502 });
  }
}