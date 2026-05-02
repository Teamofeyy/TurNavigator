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

import type { RoutePoint } from '@/lib/types'

interface RouteMapClientProps {
  mapKey: string
  routePoints: RoutePoint[]
  geometry: LatLngTuple[]
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

function buildBounds(routePoints: RoutePoint[], geometry: LatLngTuple[]): LatLngTuple[] {
  if (geometry.length > 0) {
    return geometry
  }

  return routePoints.map((point) => [point.latitude, point.longitude] satisfies LatLngTuple)
}

export function RouteMapClient({ mapKey, routePoints, geometry }: RouteMapClientProps) {
  const bounds = buildBounds(routePoints, geometry)

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

      {routePoints.map((point, index) => {
        const isFirst = index === 0
        const isLast = index === routePoints.length - 1

        return (
          <CircleMarker
            key={point.poi_id}
            center={[point.latitude, point.longitude]}
            radius={isFirst || isLast ? 12 : 10}
            pathOptions={{
              color: isFirst ? '#166534' : isLast ? '#92400e' : '#2f7d44',
              fillColor: isFirst ? '#22c55e' : isLast ? '#f59e0b' : '#ffffff',
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
