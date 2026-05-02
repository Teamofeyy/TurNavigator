'use client'

import { CompassIcon, LoaderIcon } from '@/components/ui/icons'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import { CitySelector } from './city-selector'
import { InterestSelector } from './interest-selector'
import { SegmentedControl } from './segmented-control'
import type { City, PlanningState } from '@/lib/types'

interface PlanningSidebarProps {
  cities: City[]
  citiesLoading: boolean
  state: PlanningState
  onChange: (updates: Partial<PlanningState>) => void
  onGenerate: () => void
  isGenerating: boolean
}

const budgetOptions = [
  { value: 'low' as const, label: 'Эконом' },
  { value: 'medium' as const, label: 'Средний' },
  { value: 'high' as const, label: 'Высокий' },
]

const paceOptions = [
  { value: 'relaxed' as const, label: 'Спокойный' },
  { value: 'moderate' as const, label: 'Умеренный' },
  { value: 'intensive' as const, label: 'Активный' },
]

const transportOptions = [
  { value: 'walking' as const, label: 'Пешком' },
  { value: 'public_transport' as const, label: 'Транспорт' },
  { value: 'car' as const, label: 'Авто' },
  { value: 'mixed' as const, label: 'Смешанный' },
]

const explanationOptions = [
  { value: 'short' as const, label: 'Кратко' },
  { value: 'detailed' as const, label: 'Подробно' },
]

export function PlanningSidebar({
  cities,
  citiesLoading,
  state,
  onChange,
  onGenerate,
  isGenerating,
}: PlanningSidebarProps) {
  const canGenerate = state.selectedCity && state.interests.length > 0

  return (
    <aside className="w-full shrink-0 border-b border-stone-200 bg-white lg:sticky lg:top-0 lg:h-screen lg:border-r lg:border-b-0">
      <div className="flex flex-col lg:h-screen">
        {/* Header */}
        <div className="px-5 py-5 border-b border-stone-200">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-emerald-600 text-white">
              <CompassIcon className="h-5 w-5" />
            </div>
            <div>
              <h1 className="font-semibold text-lg text-stone-900">ТравелКонтекст</h1>
              <p className="text-xs text-stone-500">Планирование маршрутов</p>
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className="p-5 space-y-6 lg:flex-1 lg:overflow-y-auto">
          {/* City */}
          <div className="space-y-2">
            <Label className="text-sm font-medium text-stone-700">Город</Label>
            <CitySelector
              cities={cities}
              selectedCity={state.selectedCity}
              onSelect={(city) => onChange({ selectedCity: city })}
              isLoading={citiesLoading}
            />
          </div>

          {/* Interests */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label className="text-sm font-medium text-stone-700">Интересы</Label>
              {state.interests.length > 0 && (
                <span className="text-xs text-emerald-600 font-medium">
                  {state.interests.length} выбрано
                </span>
              )}
            </div>
            <InterestSelector
              selected={state.interests}
              onChange={(interests) => onChange({ interests })}
            />
          </div>

          <hr className="border-stone-200" />

          {/* Days and Hours */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label className="text-sm font-medium text-stone-700">Дней</Label>
              <div className="flex items-center gap-2">
                <Slider
                  value={[state.daysCount]}
                  onValueChange={([v]) => onChange({ daysCount: v })}
                  min={1}
                  max={7}
                  step={1}
                  className="flex-1"
                />
                <span className="min-w-8 text-center font-semibold text-sm text-stone-900 bg-stone-100 rounded px-2 py-1">
                  {state.daysCount}
                </span>
              </div>
            </div>
            <div className="space-y-2">
              <Label className="text-sm font-medium text-stone-700">Часов/день</Label>
              <div className="flex items-center gap-2">
                <Slider
                  value={[state.dailyTimeLimit]}
                  onValueChange={([v]) => onChange({ dailyTimeLimit: v })}
                  min={2}
                  max={12}
                  step={1}
                  className="flex-1"
                />
                <span className="min-w-8 text-center font-semibold text-sm text-stone-900 bg-stone-100 rounded px-2 py-1">
                  {state.dailyTimeLimit}
                </span>
              </div>
            </div>
          </div>

          {/* Budget */}
          <div className="space-y-2">
            <Label className="text-sm font-medium text-stone-700">Бюджет</Label>
            <SegmentedControl
              options={budgetOptions}
              value={state.budgetLevel}
              onChange={(v) => onChange({ budgetLevel: v })}
            />
            <div className="flex items-center gap-3 pt-1">
              <Slider
                value={[state.maxBudget]}
                onValueChange={([v]) => onChange({ maxBudget: v })}
                min={1000}
                max={50000}
                step={1000}
                className="flex-1"
              />
              <span className="min-w-20 text-right font-semibold text-stone-900">
                {(state.maxBudget / 1000).toFixed(0)} тыс.
              </span>
            </div>
          </div>

          {/* Pace */}
          <div className="space-y-2">
            <Label className="text-sm font-medium text-stone-700">Темп</Label>
            <SegmentedControl
              options={paceOptions}
              value={state.pace}
              onChange={(v) => onChange({ pace: v })}
            />
          </div>

          {/* Walking Distance */}
          <div className="space-y-2">
            <Label className="text-sm font-medium text-stone-700">Пешком за день (км)</Label>
            <div className="flex items-center gap-3">
              <Slider
                value={[state.maxWalkingDistance]}
                onValueChange={([v]) => onChange({ maxWalkingDistance: v })}
                min={1}
                max={20}
                step={1}
                className="flex-1"
              />
              <span className="min-w-12 text-right font-semibold text-stone-900">
                {state.maxWalkingDistance} км
              </span>
            </div>
          </div>

          {/* Transport */}
          <div className="space-y-2">
            <Label className="text-sm font-medium text-stone-700">Транспорт</Label>
            <SegmentedControl
              options={transportOptions}
              value={state.preferredTransport}
              onChange={(v) => onChange({ preferredTransport: v })}
            />
          </div>

          {/* Explanation */}
          <div className="space-y-2">
            <Label className="text-sm font-medium text-stone-700">Детальность</Label>
            <SegmentedControl
              options={explanationOptions}
              value={state.explanationLevel}
              onChange={(v) => onChange({ explanationLevel: v })}
            />
          </div>
        </div>

        {/* Generate Button */}
        <div className="border-t border-stone-200 p-5">
          <Button
            onClick={onGenerate}
            disabled={!canGenerate || isGenerating}
            className="w-full h-11 font-semibold"
            size="lg"
          >
            {isGenerating ? (
              <>
                <LoaderIcon className="mr-2 h-4 w-4" />
                Генерация...
              </>
            ) : (
              'Построить маршрут'
            )}
          </Button>
          {!canGenerate && (
            <p className="text-xs text-stone-500 text-center mt-2">
              Выберите город и интересы
            </p>
          )}
        </div>
      </div>
    </aside>
  )
}
