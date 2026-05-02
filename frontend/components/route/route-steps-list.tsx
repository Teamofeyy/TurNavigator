'use client'

import { RouteStepCard } from './route-step-card'
import type { RoutePoint } from '@/lib/types'

interface RouteStepsListProps {
  points: RoutePoint[]
}

export function RouteStepsList({ points }: RouteStepsListProps) {
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
        />
      ))}
    </div>
  )
}
