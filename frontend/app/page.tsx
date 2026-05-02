import { TravelContextApp } from '@/components/travel-context-app'
import { requestBackend } from '@/lib/backend-api'
import type { City } from '@/lib/types'

async function getInitialCities(): Promise<City[]> {
  try {
    const response = await requestBackend('/cities')
    if (!response.ok) {
      return []
    }
    return response.json()
  } catch {
    return []
  }
}

export default async function Page() {
  const cities = await getInitialCities()

  return <TravelContextApp initialCities={cities} />
}
