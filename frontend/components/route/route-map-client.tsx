'use client'

import { useEffect } from 'react'
import type { LatLngTuple } from 'leaflet'
import {
  CircleMarker,
  MapContainer,
  Polyline,
  Popup,
  TileLayer,
  useMap,
} from 'react-leaflet'

import type { RoutePoint, TripLocation } from '@/lib/types'

interface RouteMapClientProps {
  mapKey: string
  routePoints: RoutePoint[]
  geometry: LatLngTuple[]
  startLocation: TripLocation | null
  endLocation: TripLocation | null
}

function MapBehavior() {
  const map = useMap()

  useEffect(() => {
    map.attributionControl.setPrefix('')
    map.attributionControl.setPosition('bottomright')
    map.zoomControl.setPosition('topright')

    const resizeTimer = window.setTimeout(() => {
      map.invalidateSize()
    }, 50)

    return () => {
      window.clearTimeout(resizeTimer)
    }
  }, [map])

  return null
}

function buildBounds(
  routePoints: RoutePoint[],
  geometry: LatLngTuple[],
  startLocation: TripLocation | null,
  endLocation: TripLocation | null,
): LatLngTuple[] {
  if (geometry.length > 0) {
    return geometry
  }

  const points = routePoints.map((point) => [point.latitude, point.longitude] satisfies LatLngTuple)
  if (startLocation) {
    points.unshift([startLocation.latitude, startLocation.longitude])
  }
  if (endLocation) {
    points.push([endLocation.latitude, endLocation.longitude])
  }
  return points
}

export function RouteMapClient({
  mapKey,
  routePoints,
  geometry,
  startLocation,
  endLocation,
}: RouteMapClientProps) {
  const bounds = buildBounds(routePoints, geometry, startLocation, endLocation)
  const isRoundTrip =
    Boolean(startLocation && endLocation) &&
    startLocation?.latitude === endLocation?.latitude &&
    startLocation?.longitude === endLocation?.longitude &&
    startLocation?.address === endLocation?.address

  return (
    <MapContainer
      key={mapKey}
      bounds={bounds}
      boundsOptions={{ padding: [32, 32] }}
      zoomControl
      scrollWheelZoom
      doubleClickZoom
      dragging
      className="h-[480px] w-full"
    >
      <MapBehavior />

      <TileLayer
        attribution="&copy; OpenStreetMap contributors"
        url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {geometry.length > 1 && (
        <Polyline
          positions={geometry}
          pathOptions={{
            color: '#2f7d44',
            weight: 5,
            opacity: 0.88,
            lineCap: 'round',
            lineJoin: 'round',
          }}
        />
      )}

      {startLocation && (
        <CircleMarker
          center={[startLocation.latitude, startLocation.longitude]}
          radius={11}
          pathOptions={{
            color: isRoundTrip ? '#1d4ed8' : '#166534',
            fillColor: isRoundTrip ? '#60a5fa' : '#22c55e',
            fillOpacity: 1,
            weight: 3,
          }}
        >
          <Popup>
            <div className="space-y-1">
              <div className="text-sm font-semibold">
                {isRoundTrip ? 'Старт и финиш' : 'Старт'}: {startLocation.name || 'Отель'}
              </div>
              <div className="text-xs text-stone-600">{startLocation.address}</div>
            </div>
          </Popup>
        </CircleMarker>
      )}

      {endLocation && !isRoundTrip && (
        <CircleMarker
          center={[endLocation.latitude, endLocation.longitude]}
          radius={11}
          pathOptions={{
            color: '#92400e',
            fillColor: '#f59e0b',
            fillOpacity: 1,
            weight: 3,
          }}
        >
          <Popup>
            <div className="space-y-1">
              <div className="text-sm font-semibold">Финиш: {endLocation.name || 'Финальная точка'}</div>
              <div className="text-xs text-stone-600">{endLocation.address}</div>
            </div>
          </Popup>
        </CircleMarker>
      )}

      {routePoints.map((point) => {
        return (
          <CircleMarker
            key={point.poi_id}
            center={[point.latitude, point.longitude]}
            radius={10}
            pathOptions={{
              color: '#2f7d44',
              fillColor: '#ffffff',
              fillOpacity: 1,
              weight: 3,
            }}
          >
            <Popup>
              <div className="space-y-1">
                <div className="text-sm font-semibold">{point.order}. {point.name}</div>
                <div className="text-xs text-stone-600">{point.poi.address}</div>
                <div className="text-xs text-stone-600">
                  {point.visit_minutes} мин, {point.estimated_cost_rub.toLocaleString('ru-RU')} руб.
                </div>
              </div>
            </Popup>
          </CircleMarker>
        )
      })}
    </MapContainer>
  )
}
