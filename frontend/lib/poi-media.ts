import type { POI, POIImage } from '@/lib/types'

function buildWikimediaFilePathFallback(rawUrl: string): string | null {
  try {
    const url = new URL(rawUrl)
    if (
      url.hostname !== 'upload.wikimedia.org' ||
      !url.pathname.includes('/wikipedia/commons/thumb/')
    ) {
      return null
    }

    const segments = url.pathname.split('/').filter(Boolean)
    const fileNameSegment = segments.at(-2)
    const sizeSegment = segments.at(-1) ?? ''
    const widthMatch = sizeSegment.match(/^(\d+)px-/)

    if (!fileNameSegment) {
      return null
    }

    let fileName = fileNameSegment
    try {
      fileName = decodeURIComponent(fileNameSegment)
    } catch {
      // Keep malformed external values usable instead of dropping the image.
    }

    const fallbackUrl = new URL(
      `https://commons.wikimedia.org/wiki/Special:FilePath/${encodeURIComponent(fileName)}`,
    )
    if (widthMatch?.[1]) {
      fallbackUrl.searchParams.set('width', widthMatch[1])
    }
    return fallbackUrl.toString()
  } catch {
    return null
  }
}

function candidateImageUrls(image: POIImage | null | undefined): string[] {
  if (!image) {
    return []
  }
  const urls = [image.thumbnail_url, image.original_url].filter(
    (value): value is string => Boolean(value),
  )
  return urls.flatMap((url) => [url, buildWikimediaFilePathFallback(url)].filter(Boolean) as string[])
}

export function getPoiImageCandidates(poi: POI): string[] {
  const primaryCandidates = candidateImageUrls(poi.primary_image)
  const galleryCandidates = poi.images.flatMap((image) => candidateImageUrls(image))
  return [...new Set([...primaryCandidates, ...galleryCandidates])]
}

export function getPoiImageUrl(poi: POI): string | null {
  return getPoiImageCandidates(poi)[0] ?? null
}

export function getPoiImageProxyUrl(rawUrl: string | null): string | null {
  if (!rawUrl) {
    return null
  }
  if (rawUrl.startsWith('https://commons.wikimedia.org/wiki/Special:FilePath/')) {
    return rawUrl
  }
  return `/api/poi-image?src=${encodeURIComponent(rawUrl)}`
}

export function getPoiImageAttribution(poi: POI): string | null {
  const image = poi.primary_image ?? poi.images[0] ?? null
  return image?.attribution_text ?? image?.license ?? null
}
