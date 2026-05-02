'use client'

import { useCallback, useState } from 'react'

import { PlanningSidebar } from '@/components/planning/planning-sidebar'
import { MainWorkspace } from '@/components/workspace/main-workspace'
import { api } from '@/lib/api'
import type { City, PlanningState, Recommendation, Route, TabType } from '@/lib/types'

const baseState: Omit<PlanningState, 'selectedCity'> = {
  interests: ['history', 'culture', 'food'],
  budgetLevel: 'medium',
  maxBudget: 12000,
  pace: 'moderate',
  maxWalkingDistance: 8,
  preferredTransport: 'walking',
  explanationLevel: 'detailed',
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
  }))
  const [activeTab, setActiveTab] = useState<TabType>('context')

  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [route, setRoute] = useState<Route | null>(null)
  const [hasGenerated, setHasGenerated] = useState(false)

  const [isGenerating, setIsGenerating] = useState(false)
  const [loadingMessage, setLoadingMessage] = useState('')

  const handleStateChange = useCallback((updates: Partial<PlanningState>) => {
    const shouldResetGeneratedResult =
      ('selectedCity' in updates && updates.selectedCity?.id !== state.selectedCity?.id) ||
      'interests' in updates ||
      'budgetLevel' in updates ||
      'maxBudget' in updates ||
      'pace' in updates ||
      'maxWalkingDistance' in updates ||
      'preferredTransport' in updates ||
      'daysCount' in updates ||
      'dailyTimeLimit' in updates

    if (shouldResetGeneratedResult) {
      setRecommendations([])
      setRoute(null)
      setHasGenerated(false)
      setActiveTab('context')
    }
    setState((prev) => ({ ...prev, ...updates }))
  }, [state.selectedCity?.id])

  const handleGenerate = useCallback(async () => {
    if (!state.selectedCity) return

    setIsGenerating(true)
    setLoadingMessage('Создание запроса на поездку...')

    try {
      const tripRequest = await api.createTripRequest({
        city_id: state.selectedCity.id,
        profile: {
          interests: state.interests,
          budget_level: state.budgetLevel,
          max_budget: state.maxBudget,
          pace: state.pace,
          max_walking_distance_km: state.maxWalkingDistance,
          preferred_transport: state.preferredTransport,
          explanation_level: state.explanationLevel,
        },
        days_count: state.daysCount,
        daily_time_limit_hours: state.dailyTimeLimit,
        selected_interests: state.interests,
        constraints: {
          include_accommodation: false,
        },
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
      })
      setRoute(routeResponse)

      setHasGenerated(true)
      setActiveTab('recommendations')
    } catch (error) {
      console.error('[v0] Error generating trip:', error)
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
        state={state}
        onChange={handleStateChange}
        onGenerate={handleGenerate}
        isGenerating={isGenerating}
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
