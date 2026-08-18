import { NextResponse } from "next/server";

// const API_HOST = "localhost:8000";
const API_HOST = "waiver_watcher_backend:8000";

export async function GET() {
  try {
    const backend_healthy = await fetch(`http://${API_HOST}/health`);
    const backend_healthy_result = (await backend_healthy.json()) as {
      status: "healthy" | "unhealthy";
    };
    if (backend_healthy_result.status === "healthy") {
      return NextResponse.json({ status: "healthy" }, { status: 200 });
    }
    return NextResponse.json({ status: "unhealthy" }, { status: 500 });
  } catch {
    return NextResponse.json({ status: "unhealthy" }, { status: 500 });
  }
}
