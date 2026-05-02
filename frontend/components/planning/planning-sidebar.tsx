'use client'

import { CompassIcon, LoaderIcon } from '@/components/ui/icons'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { cn } from '@/lib/utils'
import {
  ACCESSIBILITY_OPTIONS,
  PROFILE_GOALS,
  TIME_WINDOW_OPTIONS,
  type City,
  type POI,
  type PlanningState,
} from '@/lib/types'
import { CitySelector } from './city-selector'
import { InterestSelector } from './interest-selector'
import { PartnerRequestDialog } from './partner-request-dialog'
import { SegmentedControl } from './segmented-control'

interface PlanningSidebarProps {
  cities: City[]
  citiesLoading: boolean
  hotels: POI[]
  hotelsLoading: boolean
  state: PlanningState
  onChange: (updates: Partial<PlanningState>) => void
  onGenerate: () => void
  isGenerating: boolean
  errorMessage: string | null
}

interface ToggleOption<T extends string> {
  id: T
  label: string
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

const compromiseOptions = [
  { value: 'balanced' as const, label: 'Баланс' },
  { value: 'budget_first' as const, label: 'Бюджет' },
  { value: 'time_first' as const, label: 'Время' },
  { value: 'experience_first' as const, label: 'Опыт' },
]

const trustOptions = [
  { value: 'low' as const, label: 'Проверяю сам' },
  { value: 'medium' as const, label: 'Советуем вместе' },
  { value: 'high' as const, label: 'Доверяю системе' },
]

export function PlanningSidebar({
  cities,
  citiesLoading,
  hotels,
  hotelsLoading,
  state,
  onChange,
  onGenerate,
  isGenerating,
  errorMessage,
}: PlanningSidebarProps) {
  const canGenerate = state.selectedCity && state.interests.length > 0

  return (
    <aside className="w-full shrink-0 border-b border-stone-200 bg-white lg:sticky lg:top-0 lg:h-screen lg:border-r lg:border-b-0">
      <div className="flex flex-col lg:h-screen">
        <div className="border-b border-stone-200 px-5 py-5">
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-600 text-white">
                <CompassIcon className="h-5 w-5" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-stone-900">ТравелКонтекст</h1>
                <p className="text-xs text-stone-500">Планирование маршрутов</p>
              </div>
            </div>

            <PartnerRequestDialog defaultCityName={state.selectedCity?.name ?? ''} />
          </div>
        </div>

        <div className="space-y-6 p-5 lg:flex-1 lg:overflow-y-auto">
          <div className="space-y-2">
            <Label className="text-sm font-medium text-stone-700">Город</Label>
            <CitySelector
              cities={cities}
              selectedCity={state.selectedCity}
              onSelect={(city) =>
                onChange({
                  selectedCity: city,
                  selectedHotel: null,
                  hotelAddress: '',
                })}
              isLoading={citiesLoading}
            />
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label className="text-sm font-medium text-stone-700">Отель и старт маршрута</Label>
              {hotelsLoading && <span className="text-xs text-stone-500">Загрузка...</span>}
            </div>

            <Select
              value={state.selectedHotel ? String(state.selectedHotel.id) : 'none'}
              onValueChange={(value) => {
                if (value === 'none') {
                  onChange({
                    selectedHotel: null,
                    hotelAddress: '',
                  })
                  return
                }

                const hotel = hotels.find((item) => item.id === Number(value))
                if (!hotel) {
                  return
                }

                onChange({
                  selectedHotel: hotel,
                  hotelAddress: hotel.address,
                })
              }}
            >
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Выберите отель из каталога" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">Без выбранного отеля</SelectItem>
                {hotels.map((hotel) => (
                  <SelectItem key={hotel.id} value={String(hotel.id)}>
                    {hotel.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Input
              value={state.hotelAddress}
              readOnly
              placeholder={
                hotelsLoading
                  ? 'Подбираем доступные варианты размещения...'
                  : hotels.length > 0
                    ? 'Адрес выбранного отеля появится здесь'
                    : 'В каталоге пока нет accommodation для этого города'
              }
            />
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label className="text-sm font-medium text-stone-700">Интересы</Label>
              {state.interests.length > 0 && (
                <span className="text-xs font-medium text-emerald-600">
                  {state.interests.length} выбрано
                </span>
              )}
            </div>
            <InterestSelector
              selected={state.interests}
              onChange={(interests) => onChange({ interests })}
            />
          </div>

          <div className="space-y-2">
            <Label className="text-sm font-medium text-stone-700">Цели поездки</Label>
            <ToggleChipGroup
              options={PROFILE_GOALS}
              selected={state.goals}
              onToggle={(goal) =>
                onChange({
                  goals: toggleArrayValue(state.goals, goal),
                })}
            />
          </div>

          <div className="space-y-2">
            <Label className="text-sm font-medium text-stone-700">Must-have</Label>
            <Textarea
              value={state.mustHave}
              onChange={(event) => onChange({ mustHave: event.target.value })}
              placeholder="По одному пожеланию в строке: вид на реку, кофейня утром, рынок с локальной едой..."
              className="min-h-24 resize-y"
            />
          </div>

          <div className="space-y-2">
            <Label className="text-sm font-medium text-stone-700">Чего избегать</Label>
            <Textarea
              value={state.avoid}
              onChange={(event) => onChange({ avoid: event.target.value })}
              placeholder="Например: крутые лестницы, шумные ТЦ, длинные пересадки..."
              className="min-h-24 resize-y"
            />
          </div>

          <hr className="border-stone-200" />

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
                <span className="min-w-8 rounded bg-stone-100 px-2 py-1 text-center text-sm font-semibold text-stone-900">
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
                <span className="min-w-8 rounded bg-stone-100 px-2 py-1 text-center text-sm font-semibold text-stone-900">
                  {state.dailyTimeLimit}
                </span>
              </div>
            </div>
          </div>

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

          <div className="space-y-2">
            <Label className="text-sm font-medium text-stone-700">Темп</Label>
            <SegmentedControl
              options={paceOptions}
              value={state.pace}
              onChange={(v) => onChange({ pace: v })}
            />
          </div>

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

          <div className="space-y-2">
            <Label className="text-sm font-medium text-stone-700">Транспорт</Label>
            <SegmentedControl
              options={transportOptions}
              value={state.preferredTransport}
              onChange={(v) => onChange({ preferredTransport: v })}
            />
          </div>

          <div className="space-y-2">
            <Label className="text-sm font-medium text-stone-700">Детальность объяснения</Label>
            <SegmentedControl
              options={explanationOptions}
              value={state.explanationLevel}
              onChange={(v) => onChange({ explanationLevel: v })}
            />
          </div>

          <div className="space-y-2">
            <Label className="text-sm font-medium text-stone-700">Стратегия компромиссов</Label>
            <SegmentedControl
              options={compromiseOptions}
              value={state.compromiseStrategy}
              onChange={(value) => onChange({ compromiseStrategy: value })}
            />
          </div>

          <div className="space-y-2">
            <Label className="text-sm font-medium text-stone-700">Уровень доверия системе</Label>
            <SegmentedControl
              options={trustOptions}
              value={state.trustLevel}
              onChange={(value) => onChange({ trustLevel: value })}
            />
          </div>

          <div className="space-y-2">
            <Label className="text-sm font-medium text-stone-700">Accessibility needs</Label>
            <ToggleChipGroup
              options={ACCESSIBILITY_OPTIONS}
              selected={state.accessibilityNeeds}
              onToggle={(value) =>
                onChange({
                  accessibilityNeeds: toggleArrayValue(state.accessibilityNeeds, value),
                })}
            />
          </div>

          <div className="space-y-2">
            <Label className="text-sm font-medium text-stone-700">Предпочтительные окна времени</Label>
            <ToggleChipGroup
              options={TIME_WINDOW_OPTIONS}
              selected={state.preferredTimeWindows}
              onToggle={(value) =>
                onChange({
                  preferredTimeWindows: toggleArrayValue(state.preferredTimeWindows, value),
                })}
            />
          </div>
        </div>

        <div className="border-t border-stone-200 p-5">
          {errorMessage && (
            <div className="mb-3 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {errorMessage}
            </div>
          )}

          <Button
            onClick={onGenerate}
            disabled={!canGenerate || isGenerating}
            className="h-11 w-full font-semibold"
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
            <p className="mt-2 text-center text-xs text-stone-500">
              Выберите город и интересы
            </p>
          )}
        </div>
      </div>
    </aside>
  )
}

function ToggleChipGroup<T extends string>({
  options,
  selected,
  onToggle,
}: {
  options: readonly ToggleOption<T>[]
  selected: readonly T[]
  onToggle: (value: T) => void
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((option) => {
        const isActive = selected.includes(option.id)
        return (
          <button
            key={option.id}
            type="button"
            onClick={() => onToggle(option.id)}
            className={cn(
              'rounded-full border px-3 py-1.5 text-sm transition-colors',
              isActive
                ? 'border-emerald-200 bg-emerald-50 text-emerald-700'
                : 'border-stone-200 bg-white text-stone-600 hover:border-stone-300 hover:text-stone-900',
            )}
          >
            {option.label}
          </button>
        )
      })}
    </div>
  )
}

function toggleArrayValue<T extends string>(items: readonly T[], value: T): T[] {
  return items.includes(value) ? items.filter((item) => item !== value) : [...items, value]
}
