import { NextRequest } from 'next/server'

import { forwardBackendJson } from '@/lib/backend-proxy'

export async function GET(request: NextRequest) {
  const search = request.nextUrl.searchParams.toString()
  const suffix = search ? `?${search}` : ''
  return forwardBackendJson(`/profiles${suffix}`)
}

export async function POST(request: NextRequest) {
  const body = await request.text()

  return forwardBackendJson('/profiles', {
    method: 'POST',
    body,
    headers: {
      'content-type': 'application/json',
    },
  })
}
