import { forwardBackendJson } from '@/lib/backend-proxy'

export async function GET() {
  return forwardBackendJson('/cities')
}
