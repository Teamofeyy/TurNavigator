'use client'

import { useCallback, useEffect, useState } from 'react'

import { PlanningSidebar } from '@/components/planning/planning-sidebar'
import { MainWorkspace } from '@/components/workspace/main-workspace'
import { api } from '@/lib/api'
import type {
  City,
  PlanningState,
  POI,
  Recommendation,
  Route,
  TabType,
  TripLocation,
  TripProfile,
} from '@/lib/types'

const baseState: Omit<PlanningState, 'selectedCity' | 'selectedHotel'> = {
  hotelAddress: '',
  interests: ['history', 'culture', 'food'],
  goals: ['discover_local_culture', 'maximize_variety'],
  mustHave: '',
  avoid: '',
  budgetLevel: 'medium',
  maxBudget: 12000,
  pace: 'moderate',
  maxWalkingDistance: 8,
  preferredTransport: 'walking',
  explanationLevel: 'detailed',
  compromiseStrategy: 'balanced',
  trustLevel: 'medium',
  accessibilityNeeds: [],
  preferredTimeWindows: ['morning', 'evening'],
  daysCount: 2,
  dailyTimeLimit: 8,
}

function getDefaultCity(cities: City[]): City | null {
  return cities.find((city) => city.external_id === 'rostov-on-don') ?? cities[0] ?? null
}

interface TravelContextAppProps {
  initialCities: City[]
}

export function TravelContextApp({ initialCities }: TravelContextAppProps) {
  const [cities] = useState<City[]>(initialCities)
  const [state, setState] = useState<PlanningState>(() => ({
    ...baseState,
    selectedCity: getDefaultCity(initialCities),
    selectedHotel: null,
  }))
  const [activeTab, setActiveTab] = useState<TabType>('context')

  const [hotels, setHotels] = useState<POI[]>([])
  const [hotelsLoading, setHotelsLoading] = useState(false)
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [route, setRoute] = useState<Route | null>(null)
  const [hasGenerated, setHasGenerated] = useState(false)

  const [isGenerating, setIsGenerating] = useState(false)
  const [loadingMessage, setLoadingMessage] = useState('')
  const [generationError, setGenerationError] = useState<string | null>(null)

  useEffect(() => {
    const cityId = state.selectedCity?.id
    if (!cityId) {
      return
    }

    let isCancelled = false

    async function loadHotels() {
      setHotelsLoading(true)

      try {
        const hotelPois = await api.getCityPois(cityId, {
          category: 'accommodation',
          limit: 80,
        })
        if (isCancelled) {
          return
        }

        setHotels(hotelPois)
        setState((prev) => {
          const nextSelectedHotel =
            prev.selectedHotel && hotelPois.some((hotel) => hotel.id === prev.selectedHotel?.id)
              ? prev.selectedHotel
              : null

          return {
            ...prev,
            selectedHotel: nextSelectedHotel,
            hotelAddress: nextSelectedHotel?.address ?? '',
          }
        })
      } catch {
        if (!isCancelled) {
          setHotels([])
        }
      } finally {
        if (!isCancelled) {
          setHotelsLoading(false)
        }
      }
    }

    void loadHotels()

    return () => {
      isCancelled = true
    }
  }, [state.selectedCity?.id])

  const handleStateChange = useCallback((updates: Partial<PlanningState>) => {
    const shouldResetGeneratedResult =
      ('selectedCity' in updates && updates.selectedCity?.id !== state.selectedCity?.id) ||
      'selectedHotel' in updates ||
      'hotelAddress' in updates ||
      'interests' in updates ||
      'goals' in updates ||
      'mustHave' in updates ||
      'avoid' in updates ||
      'budgetLevel' in updates ||
      'maxBudget' in updates ||
      'pace' in updates ||
      'maxWalkingDistance' in updates ||
      'preferredTransport' in updates ||
      'compromiseStrategy' in updates ||
      'trustLevel' in updates ||
      'accessibilityNeeds' in updates ||
      'preferredTimeWindows' in updates ||
      'daysCount' in updates ||
      'dailyTimeLimit' in updates

    if (shouldResetGeneratedResult) {
      setRecommendations([])
      setRoute(null)
      setHasGenerated(false)
      setActiveTab('context')
      setGenerationError(null)
    }
    if ('selectedCity' in updates && updates.selectedCity?.id !== state.selectedCity?.id) {
      setHotels([])
      setHotelsLoading(false)
    }
    setState((prev) => ({ ...prev, ...updates }))
  }, [state.selectedCity?.id])

  const handleGenerate = useCallback(async () => {
    if (!state.selectedCity) return

    setIsGenerating(true)
    setGenerationError(null)
    setLoadingMessage('Сохранение профиля путешественника...')

    try {
      const savedProfile = await api.createProfile(buildTripProfile(state))
      const hotelLocation = buildHotelLocation(state.selectedHotel, state.hotelAddress)

      setLoadingMessage('Создание запроса на поездку...')
      const tripRequest = await api.createTripRequest({
        city_id: state.selectedCity.id,
        profile_id: savedProfile.id,
        days_count: state.daysCount,
        daily_time_limit_hours: state.dailyTimeLimit,
        selected_interests: state.interests,
        constraints: {
          include_accommodation: false,
          return_to_start: Boolean(hotelLocation),
        },
        start_location: hotelLocation,
        end_location: hotelLocation,
      })

      setLoadingMessage('Генерация рекомендаций...')
      const recsResponse = await api.generateRecommendations({
        trip_request_id: tripRequest.id,
        limit: 12,
        include_accommodation: false,
        include_categories: null,
        exclude_categories: [],
      })
      setRecommendations(recsResponse.recommendations)

      setLoadingMessage('Построение маршрута...')
      const routePoiIds = recsResponse.recommendations
        .slice(0, 8)
        .map((recommendation) => recommendation.poi_id)
      const routeResponse = await api.buildRoute({
        trip_request_id: tripRequest.id,
        poi_ids: routePoiIds,
        max_points: routePoiIds.length || 8,
        optimize_order: true,
        strict_constraints: true,
        start_location: hotelLocation,
        end_location: hotelLocation,
      })
      setRoute(routeResponse)

      setHasGenerated(true)
      setActiveTab('recommendations')
    } catch (error) {
      console.error('[v0] Error generating trip:', error)
      setGenerationError(
        error instanceof Error
          ? error.message
          : 'Не удалось построить персональный маршрут. Попробуйте снова.',
      )
    } finally {
      setIsGenerating(false)
      setLoadingMessage('')
    }
  }, [state])

  return (
    <div className="min-h-screen bg-background lg:grid lg:grid-cols-[400px_minmax(0,1fr)]">
      <PlanningSidebar
        cities={cities}
        citiesLoading={false}
        hotels={hotels}
        hotelsLoading={hotelsLoading}
        state={state}
        onChange={handleStateChange}
        onGenerate={handleGenerate}
        isGenerating={isGenerating}
        errorMessage={generationError}
      />

      <MainWorkspace
        selectedCity={state.selectedCity}
        preferredTransport={state.preferredTransport}
        activeTab={activeTab}
        onTabChange={setActiveTab}
        recommendations={recommendations}
        route={route}
        isLoading={isGenerating}
        loadingMessage={loadingMessage}
        hasGenerated={hasGenerated}
      />
    </div>
  )
}

function buildTripProfile(state: PlanningState): TripProfile {
  return {
    interests: state.interests,
    budget_level: state.budgetLevel,
    max_budget: state.maxBudget,
    pace: state.pace,
    max_walking_distance_km: state.maxWalkingDistance,
    preferred_transport: state.preferredTransport,
    explanation_level: state.explanationLevel,
    goals: state.goals,
    must_have: splitTextList(state.mustHave),
    avoid: splitTextList(state.avoid),
    compromise_strategy: state.compromiseStrategy,
    trust_level: state.trustLevel,
    accessibility_needs: state.accessibilityNeeds,
    preferred_time_windows: state.preferredTimeWindows,
  }
}

function buildHotelLocation(selectedHotel: POI | null, hotelAddress: string): TripLocation | null {
  if (!selectedHotel || !hotelAddress) {
    return null
  }

  return {
    address: hotelAddress,
    latitude: selectedHotel.latitude,
    longitude: selectedHotel.longitude,
    name: selectedHotel.name,
    poi_id: selectedHotel.id,
  }
}

function splitTextList(value: string): string[] {
  return value
    .split(/\n|,/)
    .map((item) => item.trim())
    .filter(Boolean)
}
