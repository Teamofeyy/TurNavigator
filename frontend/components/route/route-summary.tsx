'use client'

import { RouteIcon, ClockIcon, FootprintsIcon, WalletIcon, CheckIcon } from '@/components/ui/icons'
import { Badge } from '@/components/ui/badge'
import type { Route } from '@/lib/types'

interface RouteSummaryProps {
  route: Route
}

export function RouteSummary({ route }: RouteSummaryProps) {
  const totalHours = Math.floor(route.total_time_minutes / 60)
  const totalMinutes = route.total_time_minutes % 60

  return (
    <div className="space-y-4">
      {/* Stats grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <div className="p-4 rounded-xl bg-primary/5 border border-primary/10">
          <div className="flex items-center gap-2 text-muted-foreground mb-2">
            <RouteIcon className="h-4 w-4 text-primary" />
            <span className="text-xs">Точек</span>
          </div>
          <div className="text-2xl font-semibold text-foreground">{route.route_points.length}</div>
        </div>

        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-100">
          <div className="flex items-center gap-2 text-muted-foreground mb-2">
            <FootprintsIcon className="h-4 w-4 text-emerald-600" />
            <span className="text-xs">Расстояние</span>
          </div>
          <div className="text-2xl font-semibold text-foreground">{route.total_distance_km.toFixed(1)} км</div>
        </div>

        <div className="p-4 rounded-xl bg-amber-50 border border-amber-100">
          <div className="flex items-center gap-2 text-muted-foreground mb-2">
            <ClockIcon className="h-4 w-4 text-amber-600" />
            <span className="text-xs">Время</span>
          </div>
          <div className="text-2xl font-semibold text-foreground">{totalHours}ч {totalMinutes}м</div>
        </div>

        <div className="p-4 rounded-xl bg-purple-50 border border-purple-100">
          <div className="flex items-center gap-2 text-muted-foreground mb-2">
            <WalletIcon className="h-4 w-4 text-purple-600" />
            <span className="text-xs">Бюджет</span>
          </div>
          <div className="text-2xl font-semibold text-foreground">{(route.estimated_budget / 1000).toFixed(1)}k р.</div>
        </div>
      </div>

      {/* Status badges */}
      <div className="flex items-center gap-2 flex-wrap">
        <Badge
          className={
            route.within_budget
              ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
              : 'bg-amber-50 text-amber-700 border-amber-200'
          }
        >
          <CheckIcon className="h-3 w-3 mr-1" />
          {route.within_budget ? 'В бюджете' : 'Превышает бюджет'}
        </Badge>
        <Badge
          className={
            route.within_time_limit
              ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
              : 'bg-amber-50 text-amber-700 border-amber-200'
          }
        >
          <CheckIcon className="h-3 w-3 mr-1" />
          {route.within_time_limit ? 'По времени' : 'Превышает время'}
        </Badge>
      </div>

      {/* Summary info */}
      <div className="flex flex-wrap items-center gap-x-4 gap-y-2 rounded-lg bg-muted px-4 py-3 text-sm">
        <span>
          <strong>{route.days_count}</strong>{' '}
          {route.days_count === 1 ? 'день' : route.days_count < 5 ? 'дня' : 'дней'}
        </span>
        <span className="hidden text-border sm:inline">|</span>
        <span>
          <strong>{Math.floor(route.daily_time_limit_minutes / 60)}</strong> ч/день
        </span>
        <span className="hidden text-border sm:inline">|</span>
        <span>
          <strong>{route.total_visit_minutes}</strong> мин осмотра
        </span>
      </div>

      {/* Explanation */}
      {route.explanation_summary && (
        <p className="text-sm text-muted-foreground p-4 rounded-lg bg-muted/50 border border-border">
          {route.explanation_summary}
        </p>
      )}
    </div>
  )
}
