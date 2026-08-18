import { NextResponse } from "next/server";

// const API_HOST = "localhost:8000";
const API_HOST = "waiver_watcher_backend:8000";

export async function GET() {
  console.log("Checking application health");
  try {
    const backend_healthy = await fetch(`http://${API_HOST}/health`);
    const backend_healthy_result = (await backend_healthy.json()) as {
      status: "healthy" | "unhealthy";
    };
    if (backend_healthy_result.status === "healthy") {
      console.log("Application healthy");
      return NextResponse.json({ status: "healthy" }, { status: 200 });
    }
    console.log("Application unhealthy, backend response not healthy");
    console.log(backend_healthy);
    console.log(backend_healthy_result);
    return NextResponse.json({ status: "unhealthy" }, { status: 500 });
  } catch (e) {
    console.log("Application unhealthy, error encountered");
    console.error(e);
    return NextResponse.json({ status: "unhealthy" }, { status: 500 });
  }
}
