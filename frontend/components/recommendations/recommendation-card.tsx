'use client'

import { ClockIcon, MapPinIcon, WalletIcon, StarIcon } from '@/components/ui/icons'
import { Badge } from '@/components/ui/badge'
import { PoiImage } from '@/components/media/poi-image'
import { cn } from '@/lib/utils'
import type { Recommendation } from '@/lib/types'
import { getCategoryLabel } from '@/lib/types'

interface RecommendationCardProps {
  recommendation: Recommendation
  rank: number
}

const categoryStyles: Record<string, { bg: string; text: string; border: string }> = {
  culture: { bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-200' },
  history: { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200' },
  food: { bg: 'bg-orange-50', text: 'text-orange-700', border: 'border-orange-200' },
  nature: { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' },
  architecture: { bg: 'bg-slate-50', text: 'text-slate-700', border: 'border-slate-200' },
  entertainment: { bg: 'bg-pink-50', text: 'text-pink-700', border: 'border-pink-200' },
  shopping: { bg: 'bg-cyan-50', text: 'text-cyan-700', border: 'border-cyan-200' },
  nightlife: { bg: 'bg-indigo-50', text: 'text-indigo-700', border: 'border-indigo-200' },
}

export function RecommendationCard({ recommendation, rank }: RecommendationCardProps) {
  const { poi, score, matched_interests, explanation } = recommendation
  const styles = categoryStyles[poi.category] || { bg: 'bg-muted', text: 'text-foreground', border: 'border-border' }

  return (
    <div className="bg-card rounded-xl border border-border overflow-hidden hover:shadow-lg hover:border-primary/30 transition-all">
      {/* Header with rank and score */}
      <div className={cn('flex items-center justify-between px-4 py-3 border-b', styles.bg, styles.border)}>
        <div className="flex items-center gap-3">
          <div className={cn('flex items-center justify-center w-8 h-8 rounded-lg font-semibold text-sm', styles.bg, styles.text, 'border', styles.border)}>
            {rank}
          </div>
          <Badge className={cn('text-xs font-medium', styles.bg, styles.text, 'border', styles.border)}>
            {getCategoryLabel(poi.category)}
          </Badge>
        </div>
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-card border border-border">
          <StarIcon className="h-3.5 w-3.5 text-amber-500" filled />
          <span className="text-sm font-semibold text-foreground">{(score * 100).toFixed(0)}%</span>
        </div>
      </div>

      <PoiImage
        poi={poi}
        className={cn('aspect-[16/9] border-b', styles.border)}
        imageClassName="transition-transform duration-300 hover:scale-[1.03]"
      />

      <div className="p-4 space-y-3">
        {/* Name */}
        <h3 className="font-semibold text-base text-foreground line-clamp-2">
          {poi.name}
        </h3>

        {/* Address */}
        {poi.address && (
          <p className="text-sm text-muted-foreground flex items-center gap-2">
            <MapPinIcon className="h-3.5 w-3.5 shrink-0" />
            <span className="truncate">{poi.address}</span>
          </p>
        )}

        {/* Stats */}
        <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm">
          {poi.average_cost_rub > 0 && (
            <div className="flex items-center gap-1.5 text-muted-foreground">
              <WalletIcon className="h-4 w-4" />
              <span className="font-medium text-foreground">{poi.average_cost_rub.toLocaleString('ru-RU')} р.</span>
            </div>
          )}
          {poi.estimated_visit_minutes > 0 && (
            <div className="flex items-center gap-1.5 text-muted-foreground">
              <ClockIcon className="h-4 w-4" />
              <span className="font-medium text-foreground">{poi.estimated_visit_minutes} мин</span>
            </div>
          )}
        </div>

        {/* Matched Interests */}
        {matched_interests.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {matched_interests.map((interest) => (
              <Badge key={interest} variant="outline" className="text-xs px-2 py-0.5">
                {getCategoryLabel(interest)}
              </Badge>
            ))}
          </div>
        )}

        {/* Explanation */}
        <p className="text-sm text-muted-foreground line-clamp-2">
          {explanation}
        </p>
      </div>
    </div>
  )
}
