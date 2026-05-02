'use client'

import { RouteStepCard } from './route-step-card'
import type { RoutePoint } from '@/lib/types'

interface RouteStepsListProps {
  points: RoutePoint[]
  startLabel?: string
  endLabel?: string
  returnLegDistanceKm?: number
  returnLegTravelMinutes?: number
}

export function RouteStepsList({
  points,
  startLabel,
  endLabel,
  returnLegDistanceKm = 0,
  returnLegTravelMinutes = 0,
}: RouteStepsListProps) {
  if (points.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <p className="text-muted-foreground">Нет точек маршрута</p>
      </div>
    )
  }

  return (
    <div className="space-y-0">
      {points.map((point, index) => (
        <RouteStepCard
          key={point.poi_id}
          point={point}
          isLast={index === points.length - 1}
          startLabel={startLabel}
          nextLegDistanceKm={points[index + 1]?.leg_distance_km ?? 0}
          nextLegTravelMinutes={points[index + 1]?.leg_travel_minutes ?? 0}
        />
      ))}
      {returnLegTravelMinutes > 0 && (
        <div className="ml-14 rounded-lg border border-dashed border-amber-200 bg-amber-50/70 px-4 py-3 text-sm text-amber-800">
          Возвращение {endLabel ? `в ${endLabel}` : 'к финальной точке'}: {returnLegTravelMinutes} мин (
          {returnLegDistanceKm.toFixed(1)} км)
        </div>
      )}
    </div>
  )
}
