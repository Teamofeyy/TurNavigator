'use client'

import { RecommendationCard } from './recommendation-card'
import type { Recommendation } from '@/lib/types'

interface RecommendationsListProps {
  recommendations: Recommendation[]
}

export function RecommendationsList({ recommendations }: RecommendationsListProps) {
  if (recommendations.length === 0) {
    return null
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-bold text-foreground">
          Найдено мест: <span className="text-primary">{recommendations.length}</span>
        </h3>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
        {recommendations.map((rec, index) => (
          <RecommendationCard key={rec.poi_id} recommendation={rec} rank={index + 1} />
        ))}
      </div>
    </div>
  )
}
