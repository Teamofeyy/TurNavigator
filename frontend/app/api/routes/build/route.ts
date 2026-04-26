import { NextRequest } from "next/server";

import { forwardBackendJson } from "@/lib/backend-proxy";

export async function POST(request: NextRequest) {
  const body = await request.text();

  return forwardBackendJson("/routes/build", {
    method: "POST",
    body,
    headers: {
      "content-type": "application/json",
    },
  });
}
