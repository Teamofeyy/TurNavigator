import { NextRequest, NextResponse } from 'next/server'

type Transport = 'walking' | 'public_transport' | 'car' | 'mixed'
type LatLngPair = [number, number]

interface GeometryPointInput {
  latitude: number
  longitude: number
}

interface RouteGeometryRequest {
  transport: Transport
  points: GeometryPointInput[]
}

interface OrsGeoJsonResponse {
  features?: Array<{
    geometry?: {
      coordinates?: [number, number][]
    }
  }>
}

function mapTransportToOrsProfile(transport: Transport): string {
  switch (transport) {
    case 'car':
      return 'driving-car'
    case 'walking':
      return 'foot-walking'
    case 'public_transport':
    case 'mixed':
    default:
      return 'foot-walking'
  }
}

function buildFallbackPayload(
  points: GeometryPointInput[],
  transport: Transport,
  note: string,
) {
  return {
    geometry: points.map((point) => [point.latitude, point.longitude] satisfies LatLngPair),
    source: 'fallback' as const,
    profile: transport,
    note,
  }
}

export async function POST(request: NextRequest) {
  let payload: RouteGeometryRequest

  try {
    payload = (await request.json()) as RouteGeometryRequest
  } catch {
    return NextResponse.json({ detail: 'Invalid route geometry payload.' }, { status: 400 })
  }

  const points = payload.points ?? []
  const transport = payload.transport ?? 'walking'

  if (points.length === 0) {
    return NextResponse.json({ detail: 'At least one route point is required.' }, { status: 400 })
  }

  if (points.length < 2) {
    return NextResponse.json(
      buildFallbackPayload(
        points,
        transport,
        'Для одного объекта показана только точка на карте.',
      ),
    )
  }

  const apiKey = process.env.OPENROUTESERVICE_API_KEY
  if (!apiKey) {
    return NextResponse.json(
      buildFallbackPayload(
        points,
        transport,
        'Добавьте OPENROUTESERVICE_API_KEY, чтобы маршрут строился по дорожной сети.',
      ),
    )
  }

  const orsProfile = mapTransportToOrsProfile(transport)

  try {
    const response = await fetch(
      `https://api.openrouteservice.org/v2/directions/${orsProfile}/geojson`,
      {
        method: 'POST',
        headers: {
          Authorization: apiKey,
          Accept: 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
          'Content-Type': 'application/json; charset=utf-8',
        },
        body: JSON.stringify({
          coordinates: points.map((point) => [point.longitude, point.latitude]),
          instructions: false,
        }),
        cache: 'no-store',
      },
    )

    if (!response.ok) {
      return NextResponse.json(
        buildFallbackPayload(
          points,
          transport,
          'Маршрутизатор временно недоступен, показана упрощённая линия между точками.',
        ),
      )
    }

    const data = (await response.json()) as OrsGeoJsonResponse
    const coordinates = data.features?.[0]?.geometry?.coordinates

    if (!coordinates || coordinates.length === 0) {
      return NextResponse.json(
        buildFallbackPayload(
          points,
          transport,
          'Сервис маршрутизации не вернул геометрию, показана упрощённая линия.',
        ),
      )
    }

    return NextResponse.json({
      geometry: coordinates.map(([longitude, latitude]) => [latitude, longitude] satisfies LatLngPair),
      source: 'openrouteservice' as const,
      profile: orsProfile,
      note:
        transport === 'public_transport' || transport === 'mixed'
          ? 'Для выбранного режима использован бесплатный дорожный профиль без GTFS-транзита.'
          : 'Маршрут построен по дорожной сети openrouteservice.',
    })
  } catch {
    return NextResponse.json(
      buildFallbackPayload(
        points,
        transport,
        'Не удалось получить дорожную геометрию, показана упрощённая линия.',
      ),
    )
  }
}
