import { NextResponse } from 'next/server'

import { requestBackend } from '@/lib/backend-api'

export async function forwardBackendJson(
  path: string,
  init?: RequestInit,
): Promise<NextResponse> {
  try {
    const response = await requestBackend(path, init)
    const contentType = response.headers.get('content-type') ?? ''

    if (contentType.includes('application/json')) {
      const json = await response.json()
      return NextResponse.json(json, { status: response.status })
    }

    const text = await response.text()
    return NextResponse.json(
      { detail: text || 'Backend returned an empty response.' },
      { status: response.status },
    )
  } catch {
    return NextResponse.json(
      { detail: 'Backend API is unavailable.' },
      { status: 502 },
    )
  }
}
