import { NextRequest } from "next/server";

import { forwardBackendJson } from "@/lib/backend-proxy";

type RouteContext = {
  params: Promise<{
    cityId: string;
  }>;
};

export async function GET(request: NextRequest, context: RouteContext) {
  const { cityId } = await context.params;
  const search = request.nextUrl.search || "";
  return forwardBackendJson(`/cities/${cityId}/pois${search}`);
}
