'use client'

import { ClockIcon, FootprintsIcon, WalletIcon, MapPinIcon, ArrowDownIcon } from '@/components/ui/icons'
import { Badge } from '@/components/ui/badge'
import { PoiImage } from '@/components/media/poi-image'
import { cn } from '@/lib/utils'
import type { RoutePoint } from '@/lib/types'
import { getCategoryLabel } from '@/lib/types'

interface RouteStepCardProps {
  point: RoutePoint
  isLast: boolean
  startLabel?: string
  nextLegDistanceKm?: number
  nextLegTravelMinutes?: number
}

const categoryStyles: Record<string, { bg: string; text: string }> = {
  culture: { bg: 'bg-purple-50', text: 'text-purple-700' },
  history: { bg: 'bg-amber-50', text: 'text-amber-700' },
  food: { bg: 'bg-orange-50', text: 'text-orange-700' },
  nature: { bg: 'bg-emerald-50', text: 'text-emerald-700' },
  architecture: { bg: 'bg-slate-100', text: 'text-slate-700' },
  entertainment: { bg: 'bg-pink-50', text: 'text-pink-700' },
  shopping: { bg: 'bg-cyan-50', text: 'text-cyan-700' },
  nightlife: { bg: 'bg-indigo-50', text: 'text-indigo-700' },
}

export function RouteStepCard({
  point,
  isLast,
  startLabel,
  nextLegDistanceKm = 0,
  nextLegTravelMinutes = 0,
}: RouteStepCardProps) {
  const styles = categoryStyles[point.category] || { bg: 'bg-muted', text: 'text-foreground' }
  const arrivalLabel = point.order === 1 && startLabel ? `От ${startLabel}` : 'Переход до точки'

  return (
    <div className="relative">
      {/* Step Number and Line */}
      <div className="absolute left-0 top-0 bottom-0 flex flex-col items-center w-10">
        <div className={cn('flex items-center justify-center w-10 h-10 rounded-lg text-sm font-semibold shrink-0', styles.bg, styles.text)}>
          {point.order}
        </div>
        {!isLast && (
          <div className="flex-1 w-0.5 bg-border my-2" />
        )}
      </div>

      {/* Card */}
      <div className="ml-14 pb-4">
        <div className="bg-card rounded-lg border border-border p-4 hover:shadow-md transition-shadow">
          <PoiImage
            poi={point.poi}
            className="mb-4 aspect-[16/8] rounded-xl border border-border"
            imageClassName="transition-transform duration-300 hover:scale-[1.02]"
            compact
          />
          <div className="space-y-2">
            {/* Category and name */}
            <div className="flex items-start gap-2">
              <Badge className={cn('text-xs font-medium border-0 shrink-0', styles.bg, styles.text)}>
                {getCategoryLabel(point.category)}
              </Badge>
            </div>

            <h4 className="font-semibold text-foreground line-clamp-2">
              {point.name}
            </h4>

            {point.poi.address && (
              <p className="text-sm text-muted-foreground flex items-center gap-1.5">
                <MapPinIcon className="h-3.5 w-3.5 shrink-0" />
                <span className="truncate">{point.poi.address}</span>
              </p>
            )}

            {/* Stats */}
            <div className="flex flex-wrap items-center gap-x-4 gap-y-2 pt-2 text-sm">
              <div className="flex items-center gap-1.5 text-muted-foreground">
                <ClockIcon className="h-3.5 w-3.5" />
                <span className="font-medium text-foreground">{point.visit_minutes} мин</span>
              </div>
              {point.estimated_cost_rub > 0 && (
                <div className="flex items-center gap-1.5 text-muted-foreground">
                  <WalletIcon className="h-3.5 w-3.5" />
                  <span className="font-medium text-foreground">{point.estimated_cost_rub.toLocaleString('ru-RU')} р.</span>
                </div>
              )}
              {point.leg_distance_km > 0 && (
                <div className="flex items-center gap-1.5 text-muted-foreground">
                  <FootprintsIcon className="h-3.5 w-3.5" />
                  <span className="font-medium text-foreground">
                    {arrivalLabel}: {point.leg_distance_km.toFixed(1)} км
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Travel indicator */}
        {!isLast && nextLegTravelMinutes > 0 && (
          <div className="flex items-center gap-2 mt-2 ml-2 text-xs text-muted-foreground">
            <ArrowDownIcon className="h-3 w-3" />
            <span>{nextLegTravelMinutes} мин ({nextLegDistanceKm.toFixed(1)} км)</span>
          </div>
        )}
      </div>
    </div>
  )
}
