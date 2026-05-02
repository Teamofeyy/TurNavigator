import { NextRequest } from 'next/server'

import { forwardBackendJson } from '@/lib/backend-proxy'

interface RouteContext {
  params: Promise<{
    cityId: string
  }>
}

export async function GET(request: NextRequest, context: RouteContext) {
  const { cityId } = await context.params
  const search = request.nextUrl.searchParams.toString()
  const suffix = search ? `?${search}` : ''

  return forwardBackendJson(`/cities/${cityId}/pois${suffix}`)
}
