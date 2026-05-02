'use client'

import { useMemo, useState } from 'react'

import { CameraIcon } from '@/components/ui/icons'
import { cn } from '@/lib/utils'
import type { POI } from '@/lib/types'
import { getCategoryLabel } from '@/lib/types'
import {
  getPoiImageCandidates,
  getPoiImageProxyUrl,
} from '@/lib/poi-media'

interface PoiImageProps {
  poi: POI
  className?: string
  imageClassName?: string
  overlayClassName?: string
  compact?: boolean
}

export function PoiImage({
  poi,
  className,
  imageClassName,
  overlayClassName,
  compact = false,
}: PoiImageProps) {
  const imageCandidates = useMemo(() => getPoiImageCandidates(poi), [poi])
  const [failedUrls, setFailedUrls] = useState<string[]>([])

  const activeImage = imageCandidates.find((url) => !failedUrls.includes(url)) ?? null
  const activeImageProxy = getPoiImageProxyUrl(activeImage)

  return (
    <div
      className={cn(
        'relative overflow-hidden bg-gradient-to-br from-stone-100 via-stone-50 to-emerald-50',
        className,
      )}
    >
      {activeImage && activeImageProxy ? (
        <img
          src={activeImageProxy}
          alt={poi.name}
          loading="lazy"
          className={cn('h-full w-full object-cover', imageClassName)}
          onError={() => {
            setFailedUrls((prev) => (prev.includes(activeImage) ? prev : [...prev, activeImage]))
          }}
        />
      ) : (
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(22,163,74,0.14),transparent_35%),linear-gradient(135deg,rgba(250,250,249,0.95),rgba(240,253,244,0.95))]" />
      )}

      <div
        className={cn(
          'pointer-events-none absolute inset-0 bg-gradient-to-t from-black/55 via-black/5 to-black/5',
          overlayClassName,
        )}
      />

      {!activeImage && (
        <div className="absolute left-3 top-3 inline-flex items-center gap-1.5 rounded-full border border-white/70 bg-white/85 px-3 py-1 text-[11px] font-medium text-stone-700 backdrop-blur">
          <CameraIcon className="h-3.5 w-3.5" />
          Фото пока не найдено
        </div>
      )}

      <div className="absolute inset-x-0 bottom-0 p-4 text-white">
        <div className="mb-1 text-[11px] font-semibold uppercase tracking-[0.08em] text-white/80">
          {getCategoryLabel(poi.subcategory || poi.category)}
        </div>
        <div className={cn('font-semibold leading-tight', compact ? 'text-sm' : 'text-base')}>
          {poi.name}
        </div>
      </div>
    </div>
  )
}
