import { NextResponse } from "next/server";
export async function POST(request: Request) {
  const base = process.env.FASTAPI_URL || "http://127.0.0.1:8000";
  try {
    const body = await request.json();
    const response = await fetch(`${base}/v1/forecasts`, {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body),cache:"no-store"});
    return NextResponse.json(await response.json(), {status:response.status});
  } catch { return NextResponse.json({detail:"Upstream API unavailable"},{status:502}); }
}
