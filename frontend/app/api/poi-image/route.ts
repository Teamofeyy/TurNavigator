import { NextRequest } from 'next/server'

const DEFAULT_CONTENT_TYPE = 'image/jpeg'

function isSupportedUrl(value: string): boolean {
  try {
    const url = new URL(value)
    return url.protocol === 'https:' || url.protocol === 'http:'
  } catch {
    return false
  }
}

function normalizeRemoteUrl(value: string): string {
  const url = new URL(value)
  const normalizedPath = url.pathname
    .split('/')
    .map((segment) => {
      if (!segment) {
        return segment
      }
      try {
        return encodeURIComponent(decodeURIComponent(segment))
      } catch {
        return encodeURIComponent(segment)
      }
    })
    .join('/')
  url.pathname = normalizedPath
  return url.toString()
}

function buildWikimediaFilePathUrl(value: string): string | null {
  const url = new URL(value)
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
    // Keep the original segment if an external source supplied a malformed escape.
  }

  const redirectUrl = new URL(
    `https://commons.wikimedia.org/wiki/Special:FilePath/${encodeURIComponent(fileName)}`,
  )
  if (widthMatch?.[1]) {
    redirectUrl.searchParams.set('width', widthMatch[1])
  }
  return redirectUrl.toString()
}

function imageFetchCandidates(sourceUrl: string): string[] {
  return [
    normalizeRemoteUrl(sourceUrl),
    buildWikimediaFilePathUrl(sourceUrl),
  ].filter((url): url is string => Boolean(url))
}

export async function GET(request: NextRequest) {
  const sourceUrl = request.nextUrl.searchParams.get('src')
  if (!sourceUrl || !isSupportedUrl(sourceUrl)) {
    return new Response('Invalid image URL.', { status: 400 })
  }

  try {
    for (const remoteUrl of imageFetchCandidates(sourceUrl)) {
      const upstream = await fetch(remoteUrl, {
        headers: {
          'user-agent': 'TravelContextPrototype/0.1',
          accept: 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        },
        cache: 'force-cache',
        next: {
          revalidate: 60 * 60 * 24,
        },
      })

      const contentType = upstream.headers.get('content-type') ?? DEFAULT_CONTENT_TYPE
      if (!upstream.ok || !contentType.startsWith('image/')) {
        continue
      }

      const bytes = await upstream.arrayBuffer()

      return new Response(bytes, {
        status: 200,
        headers: {
          'content-type': contentType,
          'cache-control': 'public, max-age=86400, s-maxage=86400',
        },
      })
    }

    return new Response('Image not available.', { status: 404 })
  } catch {
    return new Response('Image proxy failed.', { status: 502 })
  }
}
