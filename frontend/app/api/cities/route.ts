import { NextRequest } from "next/server";

import { forwardBackendJson } from "@/lib/backend-proxy";

export async function GET(request: NextRequest) {
  const search = request.nextUrl.search || "";
  return forwardBackendJson(`/cities${search}`);
}
