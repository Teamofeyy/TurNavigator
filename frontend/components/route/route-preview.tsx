'use client'

import { useMemo } from 'react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { MapPinIcon, RouteIcon } from '@/components/ui/icons'
import { cn } from '@/lib/utils'
import type { Route, RoutePoint } from '@/lib/types'

interface RoutePreviewProps {
  route: Route
}

interface ProjectedPoint {
  point: RoutePoint
  x: number
  y: number
}

const VIEWBOX_WIDTH = 100
const VIEWBOX_HEIGHT = 72
const VIEWBOX_PADDING = 10

function formatCoordinate(value: number) {
  return value.toFixed(4)
}

function projectRoutePoints(points: RoutePoint[]): ProjectedPoint[] {
  if (points.length === 0) {
    return []
  }

  if (points.length === 1) {
    return [
      {
        point: points[0],
        x: VIEWBOX_WIDTH / 2,
        y: VIEWBOX_HEIGHT / 2,
      },
    ]
  }

  const longitudes = points.map((point) => point.longitude)
  const latitudes = points.map((point) => point.latitude)

  const minLongitude = Math.min(...longitudes)
  const maxLongitude = Math.max(...longitudes)
  const minLatitude = Math.min(...latitudes)
  const maxLatitude = Math.max(...latitudes)

  const longitudeSpan = Math.max(maxLongitude - minLongitude, 0.01)
  const latitudeSpan = Math.max(maxLatitude - minLatitude, 0.01)
  const drawableWidth = VIEWBOX_WIDTH - VIEWBOX_PADDING * 2
  const drawableHeight = VIEWBOX_HEIGHT - VIEWBOX_PADDING * 2

  return points.map((point) => ({
    point,
    x: VIEWBOX_PADDING + ((point.longitude - minLongitude) / longitudeSpan) * drawableWidth,
    y: VIEWBOX_PADDING + ((maxLatitude - point.latitude) / latitudeSpan) * drawableHeight,
  }))
}

function RouteMetric({
  label,
  value,
  tone = 'default',
}: {
  label: string
  value: string
  tone?: 'default' | 'accent'
}) {
  return (
    <div
      className={cn(
        'rounded-xl border p-4',
        tone === 'accent' ? 'border-primary/20 bg-primary/5' : 'border-border bg-card',
      )}
    >
      <div className="mb-1 text-xs uppercase tracking-[0.04em] text-muted-foreground">{label}</div>
      <div className="text-sm font-semibold leading-snug text-foreground">{value}</div>
    </div>
  )
}

export function RoutePreview({ route }: RoutePreviewProps) {
  const projectedPoints = useMemo(() => projectRoutePoints(route.route_points), [route.route_points])
  const polylinePoints = projectedPoints.map((point) => `${point.x},${point.y}`).join(' ')

  const firstPoint = route.route_points[0]
  const lastPoint = route.route_points[route.route_points.length - 1]

  if (!firstPoint || !lastPoint) {
    return null
  }

  return (
    <Card className="overflow-hidden border-border/80 shadow-sm">
      <CardHeader className="border-b px-5 py-5">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <div className="mb-2 flex items-center gap-2 text-sm text-muted-foreground">
              <RouteIcon className="h-4 w-4 text-primary" />
              Координатная схема маршрута
            </div>
            <CardTitle className="text-lg">Визуальный обзор перемещения по точкам</CardTitle>
            <CardDescription className="mt-1 max-w-2xl">
              Схема построена по координатам объектов маршрута. Это не уличная карта, а компактное
              гео-представление маршрута для MVP-демонстрации.
            </CardDescription>
          </div>

          <Badge className="w-fit border-primary/20 bg-primary/10 px-3 py-1 text-primary">
            {route.route_points.length} точек
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="px-5 py-5">
        <div className="grid gap-5 xl:grid-cols-[minmax(0,1.6fr)_minmax(280px,1fr)]">
          <div className="overflow-hidden rounded-2xl border border-border bg-gradient-to-br from-card to-muted/40">
            <div className="relative aspect-[16/10] min-h-[260px]">
              <svg
                viewBox={`0 0 ${VIEWBOX_WIDTH} ${VIEWBOX_HEIGHT}`}
                className="absolute inset-0 h-full w-full"
                aria-label="Координатная схема маршрута"
                role="img"
              >
                <defs>
                  <pattern
                    id="route-grid"
                    width="8"
                    height="8"
                    patternUnits="userSpaceOnUse"
                  >
                    <path d="M 8 0 L 0 0 0 8" fill="none" stroke="rgba(28,25,23,0.08)" strokeWidth="0.35" />
                  </pattern>
                  <linearGradient id="route-surface" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="rgba(255,255,255,0.9)" />
                    <stop offset="100%" stopColor="rgba(72,140,82,0.08)" />
                  </linearGradient>
                </defs>

                <rect
                  x="0"
                  y="0"
                  width={VIEWBOX_WIDTH}
                  height={VIEWBOX_HEIGHT}
                  fill="url(#route-surface)"
                />
                <rect
                  x={VIEWBOX_PADDING}
                  y={VIEWBOX_PADDING}
                  width={VIEWBOX_WIDTH - VIEWBOX_PADDING * 2}
                  height={VIEWBOX_HEIGHT - VIEWBOX_PADDING * 2}
                  rx="6"
                  fill="url(#route-grid)"
                />

                {projectedPoints.length > 1 && (
                  <polyline
                    points={polylinePoints}
                    fill="none"
                    stroke="rgba(62,126,71,0.9)"
                    strokeWidth="1.6"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                )}

                {projectedPoints.map(({ point, x, y }, index) => {
                  const isFirst = index === 0
                  const isLast = index === projectedPoints.length - 1

                  return (
                    <g key={point.poi_id}>
                      <circle
                        cx={x}
                        cy={y}
                        r={isFirst || isLast ? 3.8 : 3.2}
                        fill={isFirst ? '#15803d' : isLast ? '#b45309' : '#ffffff'}
                        stroke={isFirst ? '#166534' : isLast ? '#92400e' : '#3e7e47'}
                        strokeWidth="1.2"
                      />
                      <text
                        x={x}
                        y={y + 0.8}
                        textAnchor="middle"
                        fontSize="3.2"
                        fontWeight="700"
                        fill={isFirst || isLast ? '#ffffff' : '#1c1917'}
                      >
                        {point.order}
                      </text>
                    </g>
                  )
                })}
              </svg>

              <div className="absolute left-4 top-4 rounded-full border border-border/70 bg-background/90 px-3 py-1.5 text-xs font-medium text-muted-foreground backdrop-blur">
                Север сверху
              </div>

              <div className="absolute right-4 top-4 rounded-full border border-primary/15 bg-background/90 px-3 py-1.5 text-xs font-medium text-foreground backdrop-blur">
                {route.total_distance_km.toFixed(1)} км по маршруту
              </div>

              <div className="absolute inset-x-4 bottom-4 rounded-xl border border-border/70 bg-background/92 p-3 backdrop-blur">
                <div className="mb-1 text-xs font-medium uppercase tracking-[0.04em] text-muted-foreground">
                  Что показано
                </div>
                <p className="text-sm leading-relaxed text-muted-foreground">
                  Линия соединяет точки в том порядке, в котором пользователь проходит маршрут.
                  Зелёная точка — старт, янтарная — финал.
                </p>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-1">
              <RouteMetric label="Старт" value={firstPoint.name} tone="accent" />
              <RouteMetric label="Финиш" value={lastPoint.name} />
            </div>

            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-1">
              <RouteMetric
                label="Координаты старта"
                value={`${formatCoordinate(firstPoint.latitude)}, ${formatCoordinate(firstPoint.longitude)}`}
              />
              <RouteMetric
                label="Координаты финиша"
                value={`${formatCoordinate(lastPoint.latitude)}, ${formatCoordinate(lastPoint.longitude)}`}
              />
            </div>

            <div className="rounded-xl border border-border bg-muted/30 p-4">
              <div className="mb-3 flex items-center gap-2 text-sm font-medium text-foreground">
                <MapPinIcon className="h-4 w-4 text-primary" />
                Точки на схеме
              </div>
              <div className="flex flex-wrap gap-2">
                {route.route_points.map((point, index) => (
                  <Badge
                    key={point.poi_id}
                    variant="outline"
                    className={cn(
                      'gap-1.5 rounded-full px-2.5 py-1 text-xs',
                      index === 0 && 'border-emerald-200 bg-emerald-50 text-emerald-700',
                      index === route.route_points.length - 1 &&
                        'border-amber-200 bg-amber-50 text-amber-700',
                    )}
                  >
                    <span className="font-semibold">{point.order}</span>
                    <span className="max-w-[15rem] truncate">{point.name}</span>
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
