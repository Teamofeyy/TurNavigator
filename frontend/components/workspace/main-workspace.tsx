'use client'

import { MapPinIcon, LightbulbIcon, RouteIcon, SparkleIcon } from '@/components/ui/icons'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { RecommendationsList } from '@/components/recommendations/recommendations-list'
import { RouteFeedback } from '@/components/route/route-feedback'
import { RouteMap } from '@/components/route/route-map'
import { RouteSummary } from '@/components/route/route-summary'
import { RouteStepsList } from '@/components/route/route-steps-list'
import { EmptyState } from '@/components/shared/empty-state'
import { LoadingState } from '@/components/shared/loading-state'
import type { City, Recommendation, Route, TabType } from '@/lib/types'

interface MainWorkspaceProps {
  selectedCity: City | null
  preferredTransport: 'walking' | 'public_transport' | 'car' | 'mixed'
  activeTab: TabType
  onTabChange: (tab: TabType) => void
  recommendations: Recommendation[]
  route: Route | null
  isLoading: boolean
  loadingMessage: string
  hasGenerated: boolean
}

export function MainWorkspace({
  selectedCity,
  preferredTransport,
  activeTab,
  onTabChange,
  recommendations,
  route,
  isLoading,
  loadingMessage,
  hasGenerated,
}: MainWorkspaceProps) {
  return (
    <main className="min-w-0 bg-background">
      {/* Header */}
      <header className="border-b bg-card px-4 py-4 sm:px-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            {selectedCity ? (
              <>
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                  <MapPinIcon className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-foreground">{selectedCity.name}</h2>
                  <p className="text-sm text-muted-foreground">
                    {selectedCity.region}, {selectedCity.country}
                  </p>
                </div>
              </>
            ) : (
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted">
                  <MapPinIcon className="h-5 w-5 text-muted-foreground" />
                </div>
                <div>
                  <h2 className="font-medium text-muted-foreground">Выберите город</h2>
                  <p className="text-sm text-muted-foreground/60">для начала планирования</p>
                </div>
              </div>
            )}
          </div>

          {selectedCity && (
            <div className="flex w-fit items-center gap-2 rounded-lg bg-muted px-3 py-1.5">
              <span className="text-lg font-semibold text-primary">{selectedCity.pois_count}</span>
              <span className="text-sm text-muted-foreground">мест</span>
            </div>
          )}
        </div>
      </header>

      {/* Tabs */}
      <Tabs
        value={activeTab}
        onValueChange={(v) => onTabChange(v as TabType)}
        className="flex flex-col"
      >
        <div className="border-b bg-card px-4 pt-4 sm:px-6">
          <div className="overflow-x-auto pb-4">
            <TabsList className="flex h-auto min-w-full gap-1 rounded-lg bg-muted p-1 sm:w-fit">
              <TabsTrigger
                value="context"
                className="gap-2 whitespace-nowrap rounded-md px-3 py-2 text-sm data-[state=active]:bg-card data-[state=active]:shadow-sm"
              >
                <SparkleIcon className="h-4 w-4" />
                Контекст
              </TabsTrigger>
              <TabsTrigger
                value="recommendations"
                className="gap-2 whitespace-nowrap rounded-md px-3 py-2 text-sm data-[state=active]:bg-card data-[state=active]:shadow-sm"
              >
                <LightbulbIcon className="h-4 w-4" />
                Рекомендации
                {recommendations.length > 0 && (
                  <span className="ml-1 rounded bg-primary px-1.5 py-0.5 text-xs font-semibold text-primary-foreground">
                    {recommendations.length}
                  </span>
                )}
              </TabsTrigger>
              <TabsTrigger
                value="route"
                className="gap-2 whitespace-nowrap rounded-md px-3 py-2 text-sm data-[state=active]:bg-card data-[state=active]:shadow-sm"
              >
                <RouteIcon className="h-4 w-4" />
                Маршрут
                {route && (
                  <span className="ml-1 rounded bg-primary px-1.5 py-0.5 text-xs font-semibold text-primary-foreground">
                    {route.route_points.length}
                  </span>
                )}
              </TabsTrigger>
            </TabsList>
          </div>
        </div>

        {/* Tab Content */}
        <div>
          <TabsContent value="context" className="m-0 p-4 sm:p-6">
            {isLoading ? (
              <LoadingState message={loadingMessage} />
            ) : !selectedCity ? (
              <EmptyState
                icon={MapPinIcon}
                title="Город не выбран"
                description="Выберите город в панели слева, чтобы начать планирование"
              />
            ) : !hasGenerated ? (
              <EmptyState
                icon={SparkleIcon}
                title="Готов к планированию"
                description="Настройте параметры и нажмите «Построить маршрут»"
              />
            ) : (
              <div className="max-w-xl mx-auto">
                <div className="p-5 rounded-xl bg-primary/5 border border-primary/10">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-9 h-9 rounded-lg bg-primary/10 flex items-center justify-center">
                      <SparkleIcon className="h-5 w-5 text-primary" />
                    </div>
                    <h3 className="font-semibold text-foreground">Маршрут готов</h3>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Маршрут по городу{' '}
                    <span className="font-medium text-foreground">{selectedCity.name}</span> построен.
                    Перейдите во вкладку «Рекомендации» или «Маршрут».
                  </p>
                </div>
              </div>
            )}
          </TabsContent>

          <TabsContent value="recommendations" className="m-0 p-4 sm:p-6">
            {isLoading ? (
              <LoadingState message={loadingMessage} />
            ) : recommendations.length === 0 ? (
              <EmptyState
                icon={LightbulbIcon}
                title="Нет рекомендаций"
                description="Нажмите «Построить маршрут» для генерации рекомендаций"
              />
            ) : (
              <RecommendationsList recommendations={recommendations} />
            )}
          </TabsContent>

          <TabsContent value="route" className="m-0 p-4 sm:p-6">
            {isLoading ? (
              <LoadingState message={loadingMessage} />
            ) : !route ? (
              <EmptyState
                icon={RouteIcon}
                title="Маршрут не построен"
                description="Нажмите «Построить маршрут» для построения маршрута"
              />
            ) : (
              <div className="space-y-6">
                <RouteMap route={route} transport={preferredTransport} />
                <RouteSummary route={route} />
                <RouteFeedback route={route} />
                <div>
                  <h3 className="font-semibold text-lg mb-4 text-foreground">Пошаговый план</h3>
                  <RouteStepsList points={route.route_points} />
                </div>
              </div>
            )}
          </TabsContent>
        </div>
      </Tabs>
    </main>
  )
}
