'use client'

import dynamic from 'next/dynamic'
import { useEffect, useMemo, useState } from 'react'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { LoaderIcon, MapPinIcon, RouteIcon } from '@/components/ui/icons'
import type { Route, RoutePoint, TripLocation } from '@/lib/types'

type Transport = 'walking' | 'public_transport' | 'car' | 'mixed'
type LatLngTuple = [number, number]

interface RouteMapProps {
  route: Route
  transport: Transport
}

interface RouteGeometryResponse {
  geometry: LatLngTuple[]
  source: 'openrouteservice' | 'fallback'
  profile: string
  note: string
}

interface GeometryPointInput {
  latitude: number
  longitude: number
}

const RouteMapClient = dynamic(
  () => import('./route-map-client').then((module) => module.RouteMapClient),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-[420px] items-center justify-center rounded-2xl border border-border bg-muted/30">
        <div className="flex items-center gap-3 text-sm text-muted-foreground">
          <LoaderIcon className="h-4 w-4" />
          Подготовка карты...
        </div>
      </div>
    ),
  },
)

function buildGeometryPoints(route: Route): GeometryPointInput[] {
  const points: GeometryPointInput[] = []

  if (route.start_location) {
    points.push({
      latitude: route.start_location.latitude,
      longitude: route.start_location.longitude,
    })
  }

  points.push(
    ...route.route_points.map((point) => ({
      latitude: point.latitude,
      longitude: point.longitude,
    })),
  )

  if (route.end_location && route.route_points.length > 0) {
    points.push({
      latitude: route.end_location.latitude,
      longitude: route.end_location.longitude,
    })
  }

  return points
}

function buildFallbackGeometry(
  routePoints: RoutePoint[],
  startLocation: TripLocation | null,
  endLocation: TripLocation | null,
): LatLngTuple[] {
  const points: LatLngTuple[] = []

  if (startLocation) {
    points.push([startLocation.latitude, startLocation.longitude])
  }

  points.push(...routePoints.map((point) => [point.latitude, point.longitude] satisfies LatLngTuple))

  if (endLocation && routePoints.length > 0) {
    points.push([endLocation.latitude, endLocation.longitude])
  }

  return points
}

export function RouteMap({ route, transport }: RouteMapProps) {
  const [geometryState, setGeometryState] = useState<RouteGeometryResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const geometryPoints = useMemo(() => buildGeometryPoints(route), [route])
  const fallbackGeometry = useMemo(
    () => buildFallbackGeometry(route.route_points, route.start_location, route.end_location),
    [route.end_location, route.route_points, route.start_location],
  )

  useEffect(() => {
    let isCancelled = false

    async function loadGeometry() {
      setIsLoading(true)

      try {
        const response = await fetch('/api/routes/geometry', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            transport,
            points: geometryPoints,
          }),
        })

        if (!response.ok) {
          throw new Error('Failed to load geometry')
        }

        const geometry = (await response.json()) as RouteGeometryResponse
        if (!isCancelled) {
          setGeometryState(geometry)
        }
      } catch {
        if (!isCancelled) {
          setGeometryState({
            geometry: fallbackGeometry,
            source: 'fallback',
            profile: transport,
            note: 'Показана упрощённая линия между точками маршрута.',
          })
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false)
        }
      }
    }

    if (geometryPoints.length === 0) {
      const frameId = window.requestAnimationFrame(() => {
        setGeometryState(null)
      })
      return () => {
        window.cancelAnimationFrame(frameId)
      }
    }

    void loadGeometry()

    return () => {
      isCancelled = true
    }
  }, [fallbackGeometry, geometryPoints, route.id, transport])

  const geometry = geometryState?.geometry?.length ? geometryState.geometry : fallbackGeometry

  return (
    <Card className="overflow-hidden border-border/80 shadow-sm">
      <CardHeader className="border-b">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <div className="mb-2 flex items-center gap-2 text-sm text-muted-foreground">
              <MapPinIcon className="h-4 w-4 text-primary" />
              Интерактивная карта маршрута
            </div>
            <CardTitle className="text-lg">Маршрут на реальной карте</CardTitle>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <Badge className="border-primary/15 bg-primary/10 text-primary">
              {route.route_points.length} точек
            </Badge>
            {isLoading && (
              <Badge variant="outline">
                <LoaderIcon className="mr-1 h-3.5 w-3.5" />
                Загрузка линии
              </Badge>
            )}
            <Badge variant="outline" className="capitalize">
              {geometryState?.source === 'openrouteservice' ? 'Дорожный маршрут' : 'Базовая линия'}
            </Badge>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4 px-5 py-5">
        <RouteMapClient
          mapKey={`${route.id}-${geometryState?.source ?? 'fallback'}-${transport}`}
          routePoints={route.route_points}
          geometry={geometry}
          startLocation={route.start_location}
          endLocation={route.end_location}
        />

        <div className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-center">
          <div className="rounded-xl border border-border bg-muted/30 px-4 py-3 text-sm text-muted-foreground">
            {geometryState?.note ?? 'Маршрут отображён по координатам выбранных объектов.'}
          </div>

          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <RouteIcon className="h-4 w-4 text-primary" />
            <span>Профиль: {geometryState?.profile ?? transport}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
