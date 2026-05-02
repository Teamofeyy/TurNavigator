const DEFAULT_BACKEND_API_URL = 'http://127.0.0.1:8000'

function normalizeBaseUrl(value: string): string {
  return value.endsWith('/') ? value.slice(0, -1) : value
}

export function getBackendApiUrl(): string {
  return normalizeBaseUrl(process.env.BACKEND_API_URL ?? DEFAULT_BACKEND_API_URL)
}

export async function requestBackend(
  path: string,
  init?: RequestInit,
): Promise<Response> {
  const headers = new Headers(init?.headers)

  if (init?.body && !headers.has('content-type')) {
    headers.set('content-type', 'application/json')
  }

  return fetch(`${getBackendApiUrl()}${path}`, {
    ...init,
    headers,
    cache: 'no-store',
  })
}
