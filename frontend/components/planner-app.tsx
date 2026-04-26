"use client";

import { useMemo, useState } from "react";
import {
  BadgeCheck,
  Building2,
  Bus,
  CircleDollarSign,
  Clock3,
  Compass,
  LoaderCircle,
  MapPinned,
  Route,
  ShieldCheck,
  Sparkles,
  TreePalm,
  UtensilsCrossed,
  Warehouse,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { Slider } from "@/components/ui/slider";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import type {
  BudgetLevel,
  City,
  ExplanationLevel,
  Pace,
  RecommendationListResponse,
  RoutePlanResponse,
  Transport,
  TripRequestCreate,
  TripRequestResponse,
} from "@/lib/types";

const INTEREST_OPTIONS = [
  { value: "history", label: "История", icon: Warehouse },
  { value: "culture", label: "Культура", icon: Sparkles },
  { value: "food", label: "Еда", icon: UtensilsCrossed },
  { value: "architecture", label: "Архитектура", icon: Building2 },
  { value: "nature", label: "Природа", icon: TreePalm },
  { value: "walking", label: "Прогулки", icon: Route },
];

const paceLabels: Record<Pace, string> = {
  relaxed: "Спокойно",
  moderate: "Умеренно",
  intensive: "Насыщенно",
};

const transportLabels: Record<Transport, string> = {
  walking: "Пешком",
  public_transport: "Транспорт",
  car: "Авто",
  mixed: "Смешанно",
};

const explanationLabels: Record<ExplanationLevel, string> = {
  short: "Коротко",
  detailed: "Подробно",
};

const categoryLabels: Record<string, string> = {
  accommodation: "Проживание",
  culture: "Культура",
  entertainment: "Развлечения",
  food: "Еда",
  history: "История",
  nature: "Природа",
  shopping: "Покупки",
};

type PlannerAppProps = {
  initialCities: City[];
  loadError?: string | null;
};

type RequestState = {
  tripRequest: TripRequestResponse | null;
  recommendations: RecommendationListResponse | null;
  routePlan: RoutePlanResponse | null;
};

function deriveBudgetLevel(maxBudget: number): BudgetLevel {
  if (maxBudget <= 8000) {
    return "low";
  }
  if (maxBudget <= 18000) {
    return "medium";
  }
  return "high";
}

function formatRub(value: number): string {
  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "RUB",
    maximumFractionDigits: 0,
  }).format(value);
}

function formatPopulation(value: number): string {
  return new Intl.NumberFormat("ru-RU").format(value);
}

function formatMinutes(totalMinutes: number): string {
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;

  if (hours === 0) {
    return `${minutes} мин`;
  }

  if (minutes === 0) {
    return `${hours} ч`;
  }

  return `${hours} ч ${minutes} мин`;
}

function formatDistance(value: number): string {
  return `${value.toFixed(1)} км`;
}

function readErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  return "Не удалось выполнить запрос.";
}

function readSliderValue(
  nextValue: number | readonly number[] | undefined,
  fallback: number,
): number {
  if (Array.isArray(nextValue)) {
    return nextValue[0] ?? fallback;
  }

  if (typeof nextValue === "number") {
    return nextValue;
  }

  return fallback;
}

async function postJson<TResponse, TPayload>(
  url: string,
  payload: TPayload,
): Promise<TResponse> {
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "content-type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const data = (await response.json()) as TResponse | { detail?: string };

  if (!response.ok) {
    throw new Error(
      typeof data === "object" &&
        data !== null &&
        "detail" in data &&
        typeof data.detail === "string"
        ? data.detail
        : "Не удалось выполнить запрос.",
    );
  }

  return data as TResponse;
}

export function PlannerApp({ initialCities, loadError }: PlannerAppProps) {
  const [selectedCityId, setSelectedCityId] = useState<string>(
    initialCities[0] ? String(initialCities[0].id) : "",
  );
  const [selectedInterests, setSelectedInterests] = useState<string[]>([
    "history",
    "culture",
    "food",
  ]);
  const [budget, setBudget] = useState(12000);
  const [maxWalkingDistance, setMaxWalkingDistance] = useState(8);
  const [daysCount, setDaysCount] = useState(2);
  const [dailyTimeLimitHours, setDailyTimeLimitHours] = useState(8);
  const [pace, setPace] = useState<Pace>("moderate");
  const [transport, setTransport] = useState<Transport>("walking");
  const [explanationLevel, setExplanationLevel] =
    useState<ExplanationLevel>("detailed");
  const [includeAccommodation, setIncludeAccommodation] = useState(false);
  const [activeTab, setActiveTab] = useState("context");
  const [requestState, setRequestState] = useState<RequestState>({
    tripRequest: null,
    recommendations: null,
    routePlan: null,
  });
  const [errorMessage, setErrorMessage] = useState<string | null>(
    loadError ?? null,
  );
  const [isSubmitting, setIsSubmitting] = useState(false);

  const selectedCity = useMemo(
    () =>
      initialCities.find((city) => city.id === Number.parseInt(selectedCityId, 10)) ??
      null,
    [initialCities, selectedCityId],
  );

  const budgetLevel = useMemo(() => deriveBudgetLevel(budget), [budget]);
  const canSubmit =
    Boolean(selectedCityId) && selectedInterests.length > 0 && !isSubmitting;

  function toggleInterest(value: string, checked: boolean) {
    setSelectedInterests((current) => {
      if (checked) {
        return current.includes(value) ? current : [...current, value];
      }
      return current.filter((interest) => interest !== value);
    });
  }

  async function handleGeneratePlan() {
    if (!selectedCity) {
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      const tripPayload: TripRequestCreate = {
        city_id: selectedCity.id,
        profile: {
          interests: selectedInterests,
          budget_level: budgetLevel,
          max_budget: budget,
          pace,
          max_walking_distance_km: maxWalkingDistance,
          preferred_transport: transport,
          explanation_level: explanationLevel,
        },
        days_count: daysCount,
        daily_time_limit_hours: dailyTimeLimitHours,
        selected_interests: selectedInterests,
        constraints: {
          include_accommodation: includeAccommodation,
        },
      };

      const tripRequest = await postJson<TripRequestResponse, TripRequestCreate>(
        "/api/trip-requests",
        tripPayload,
      );
      const recommendations =
        await postJson<RecommendationListResponse, Record<string, unknown>>(
          "/api/recommendations/generate",
          {
            trip_request_id: tripRequest.id,
            limit: 6,
            include_accommodation: includeAccommodation,
            include_categories: null,
            exclude_categories: [],
          },
        );
      const routePlan = await postJson<RoutePlanResponse, Record<string, unknown>>(
        "/api/routes/build",
        {
          trip_request_id: tripRequest.id,
          max_points: Math.min(5, recommendations.recommendations.length || 5),
          optimize_order: true,
          strict_constraints: true,
        },
      );

      setRequestState({
        tripRequest,
        recommendations,
        routePlan,
      });
      setActiveTab("recommendations");
    } catch (error) {
      setErrorMessage(readErrorMessage(error));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <div className="border-b bg-white/85 backdrop-blur">
        <div className="mx-auto flex w-full max-w-[1400px] items-center justify-between gap-4 px-4 py-4 md:px-6 lg:px-8">
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <div className="flex size-9 items-center justify-center rounded-lg bg-primary/12 text-primary">
                <MapPinned className="size-4" />
              </div>
              <div className="min-w-0">
                <h1 className="truncate text-lg font-semibold text-foreground">
                  ТравелКонтекст
                </h1>
                <p className="truncate text-sm text-muted-foreground">
                  Персонализированное планирование путешествия с учётом ограничений
                </p>
              </div>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="secondary" className="gap-1.5">
              <BadgeCheck className="size-3.5" />
              {initialCities.length > 0 ? "API подключено" : "API недоступно"}
            </Badge>
            <Badge variant="outline">Next.js 16</Badge>
            <Badge variant="outline">FastAPI</Badge>
          </div>
        </div>
      </div>

      <main className="mx-auto flex w-full max-w-[1400px] flex-1 flex-col gap-6 px-4 py-6 md:px-6 lg:px-8">
        {errorMessage ? (
          <div className="rounded-lg border border-destructive/20 bg-destructive/5 px-4 py-3 text-sm text-destructive">
            {errorMessage}
          </div>
        ) : null}

        <div className="grid gap-6 xl:grid-cols-[360px_minmax(0,1fr)]">
          <aside className="h-fit rounded-lg border bg-white p-4 shadow-sm xl:sticky xl:top-6">
            <div className="space-y-1">
              <h2 className="text-base font-semibold text-foreground">
                Параметры поездки
              </h2>
              <p className="text-sm text-muted-foreground">
                Задай контекст поездки, а система подберёт рекомендации и маршрут.
              </p>
            </div>

            <Separator className="my-4" />

            <div className="space-y-5">
              <div className="space-y-2">
                <div className="flex items-center justify-between gap-2">
                  <Label htmlFor="city-select">Город</Label>
                  <Tooltip>
                    <TooltipTrigger className="text-xs text-muted-foreground underline decoration-dotted underline-offset-4">
                      seed
                    </TooltipTrigger>
                    <TooltipContent>
                      Используется стартовый набор городов из MVP-датасета.
                    </TooltipContent>
                  </Tooltip>
                </div>
                <Select
                  value={selectedCityId}
                  onValueChange={(value) => setSelectedCityId(value ?? "")}
                >
                  <SelectTrigger id="city-select" className="w-full">
                    <SelectValue placeholder="Выбери город">
                      {selectedCity?.name ?? "Выбери город"}
                    </SelectValue>
                  </SelectTrigger>
                  <SelectContent>
                    {initialCities.map((city) => (
                      <SelectItem key={city.id} value={String(city.id)}>
                        {city.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-3">
                <div className="space-y-1">
                  <Label>Интересы</Label>
                  <p className="text-xs text-muted-foreground">
                    Эти теги участвуют в ранжировании рекомендаций.
                  </p>
                </div>
                <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-1">
                  {INTEREST_OPTIONS.map((interest) => {
                    const Icon = interest.icon;
                    const checked = selectedInterests.includes(interest.value);

                    return (
                      <label
                        key={interest.value}
                        className="flex items-center gap-3 rounded-lg border border-border px-3 py-2.5 transition-colors hover:bg-muted/40"
                      >
                        <Checkbox
                          checked={checked}
                          onCheckedChange={(nextChecked) =>
                            toggleInterest(interest.value, Boolean(nextChecked))
                          }
                        />
                        <div className="flex min-w-0 flex-1 items-center gap-2">
                          <Icon className="size-4 text-muted-foreground" />
                          <span className="truncate text-sm">{interest.label}</span>
                        </div>
                      </label>
                    );
                  })}
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between gap-3">
                  <Label htmlFor="budget-input">Бюджет</Label>
                  <Badge variant="outline">{formatRub(budget)}</Badge>
                </div>
                <Slider
                  min={3000}
                  max={30000}
                  step={500}
                  value={[budget]}
                  onValueChange={(value) =>
                    setBudget(readSliderValue(value, budget))
                  }
                />
                <Input
                  id="budget-input"
                  type="number"
                  min={0}
                  step={500}
                  value={budget}
                  onChange={(event) =>
                    setBudget(Number.parseInt(event.target.value || "0", 10))
                  }
                />
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between gap-3">
                  <Label>Пешая нагрузка</Label>
                  <Badge variant="outline">{maxWalkingDistance} км</Badge>
                </div>
                <Slider
                  min={2}
                  max={15}
                  step={1}
                  value={[maxWalkingDistance]}
                  onValueChange={(value) =>
                    setMaxWalkingDistance(
                      readSliderValue(value, maxWalkingDistance),
                    )
                  }
                />
              </div>

              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-1">
                <div className="space-y-2">
                  <Label htmlFor="days-count">Дней</Label>
                  <Input
                    id="days-count"
                    type="number"
                    min={1}
                    max={14}
                    value={daysCount}
                    onChange={(event) =>
                      setDaysCount(Number.parseInt(event.target.value || "1", 10))
                    }
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="daily-hours">Часов в день</Label>
                  <Input
                    id="daily-hours"
                    type="number"
                    min={1}
                    max={16}
                    value={dailyTimeLimitHours}
                    onChange={(event) =>
                      setDailyTimeLimitHours(
                        Number.parseInt(event.target.value || "8", 10),
                      )
                    }
                  />
                </div>
              </div>

              <div className="space-y-3">
                <Label>Темп поездки</Label>
                <Tabs value={pace} onValueChange={(value) => setPace(value as Pace)}>
                  <TabsList className="grid w-full grid-cols-3">
                    {Object.entries(paceLabels).map(([value, label]) => (
                      <TabsTrigger key={value} value={value}>
                        {label}
                      </TabsTrigger>
                    ))}
                  </TabsList>
                </Tabs>
              </div>

              <div className="space-y-3">
                <Label>Транспорт</Label>
                <Tabs
                  value={transport}
                  onValueChange={(value) => setTransport(value as Transport)}
                >
                  <TabsList className="grid w-full grid-cols-2 md:grid-cols-4 xl:grid-cols-2">
                    {Object.entries(transportLabels).map(([value, label]) => (
                      <TabsTrigger key={value} value={value}>
                        {label}
                      </TabsTrigger>
                    ))}
                  </TabsList>
                </Tabs>
              </div>

              <div className="space-y-3">
                <Label>Объяснение</Label>
                <Tabs
                  value={explanationLevel}
                  onValueChange={(value) =>
                    setExplanationLevel(value as ExplanationLevel)
                  }
                >
                  <TabsList className="grid w-full grid-cols-2">
                    {Object.entries(explanationLabels).map(([value, label]) => (
                      <TabsTrigger key={value} value={value}>
                        {label}
                      </TabsTrigger>
                    ))}
                  </TabsList>
                </Tabs>
              </div>

              <label className="flex items-center gap-3 rounded-lg border border-border px-3 py-2.5">
                <Checkbox
                  checked={includeAccommodation}
                  onCheckedChange={(nextChecked) =>
                    setIncludeAccommodation(Boolean(nextChecked))
                  }
                />
                <span className="text-sm">Добавлять проживание в подборку</span>
              </label>

              <Button
                className="w-full gap-2"
                size="lg"
                disabled={!canSubmit}
                onClick={handleGeneratePlan}
              >
                {isSubmitting ? (
                  <LoaderCircle className="size-4 animate-spin" />
                ) : (
                  <Compass className="size-4" />
                )}
                Подобрать маршрут
              </Button>
            </div>
          </aside>

          <section className="min-w-0 rounded-lg border bg-white shadow-sm">
            <Tabs
              value={activeTab}
              onValueChange={setActiveTab}
              className="min-h-[760px]"
            >
              <div className="border-b px-4 py-3 md:px-6">
                <TabsList variant="line" className="w-full justify-start">
                  <TabsTrigger value="context">Контекст</TabsTrigger>
                  <TabsTrigger value="recommendations">Рекомендации</TabsTrigger>
                  <TabsTrigger value="route">Маршрут</TabsTrigger>
                </TabsList>
              </div>

              <TabsContent value="context" className="px-4 py-4 md:px-6">
                <div className="grid gap-6">
                  <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                    <MetricCard
                      icon={MapPinned}
                      label="Выбранный город"
                      value={selectedCity?.name ?? "Не выбран"}
                      supporting={
                        selectedCity
                          ? `${selectedCity.region}, ${selectedCity.country}`
                          : "Нет данных"
                      }
                    />
                    <MetricCard
                      icon={CircleDollarSign}
                      label="Бюджет"
                      value={formatRub(budget)}
                      supporting={`Уровень: ${budgetLevel}`}
                    />
                    <MetricCard
                      icon={Clock3}
                      label="Лимит времени"
                      value={`${daysCount} дн. x ${dailyTimeLimitHours} ч`}
                      supporting={`${maxWalkingDistance} км пешком в день`}
                    />
                    <MetricCard
                      icon={Bus}
                      label="Перемещение"
                      value={transportLabels[transport]}
                      supporting={paceLabels[pace]}
                    />
                  </div>

                  <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_340px]">
                    <div className="space-y-4">
                      <div>
                        <h3 className="text-sm font-semibold text-foreground">
                          Профиль поездки
                        </h3>
                        <p className="mt-1 text-sm text-muted-foreground">
                          Это структурированный контекст, который попадёт в СППР.
                        </p>
                      </div>

                      <div className="flex flex-wrap gap-2">
                        {selectedInterests.map((interest) => (
                          <Badge key={interest} variant="secondary">
                            {INTEREST_OPTIONS.find((item) => item.value === interest)
                              ?.label ?? interest}
                          </Badge>
                        ))}
                        <Badge variant="outline">{paceLabels[pace]}</Badge>
                        <Badge variant="outline">{transportLabels[transport]}</Badge>
                        <Badge variant="outline">
                          {explanationLabels[explanationLevel]}
                        </Badge>
                      </div>

                      <div className="grid gap-4 md:grid-cols-2">
                        <Card className="rounded-lg">
                          <CardHeader>
                            <CardTitle>Ограничения</CardTitle>
                            <CardDescription>
                              Ресурсы, которые учитываются при ранжировании.
                            </CardDescription>
                          </CardHeader>
                          <CardContent className="space-y-3">
                            <ProfileLine
                              label="Максимальный бюджет"
                              value={formatRub(budget)}
                            />
                            <ProfileLine
                              label="Доступное время"
                              value={`${daysCount * dailyTimeLimitHours} ч всего`}
                            />
                            <ProfileLine
                              label="Пешая нагрузка"
                              value={`${maxWalkingDistance} км`}
                            />
                            <ProfileLine
                              label="Проживание"
                              value={includeAccommodation ? "Учитывать" : "Не учитывать"}
                            />
                          </CardContent>
                        </Card>

                        <Card className="rounded-lg">
                          <CardHeader>
                            <CardTitle>Готовый контекст</CardTitle>
                            <CardDescription>
                              То, что уже есть для следующего шага: рекомендации и маршрут.
                            </CardDescription>
                          </CardHeader>
                          <CardContent className="space-y-3">
                            <ProfileLine
                              label="Trip request"
                              value={
                                requestState.tripRequest
                                  ? `#${requestState.tripRequest.id}`
                                  : "Пока не создан"
                              }
                            />
                            <ProfileLine
                              label="Рекомендации"
                              value={
                                requestState.recommendations
                                  ? `${requestState.recommendations.recommendations.length} объектов`
                                  : "Нет результата"
                              }
                            />
                            <ProfileLine
                              label="Маршрут"
                              value={
                                requestState.routePlan
                                  ? `${requestState.routePlan.route_points.length} точек`
                                  : "Не построен"
                              }
                            />
                          </CardContent>
                        </Card>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <div>
                        <h3 className="text-sm font-semibold text-foreground">
                          Города MVP-набора
                        </h3>
                        <p className="mt-1 text-sm text-muted-foreground">
                          Уже доступны для демонстрации на защите.
                        </p>
                      </div>
                      <ScrollArea className="h-[460px] rounded-lg border">
                        <div className="space-y-3 p-3">
                          {initialCities.map((city) => (
                            <CityCard
                              key={city.id}
                              city={city}
                              isActive={city.id === selectedCity?.id}
                              onSelect={() => setSelectedCityId(String(city.id))}
                            />
                          ))}
                        </div>
                      </ScrollArea>
                    </div>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="recommendations" className="px-4 py-4 md:px-6">
                {isSubmitting ? (
                  <div className="grid gap-4">
                    {Array.from({ length: 3 }).map((_, index) => (
                      <div key={index} className="rounded-lg border p-4">
                        <Skeleton className="h-5 w-40" />
                        <Skeleton className="mt-3 h-4 w-full" />
                        <Skeleton className="mt-2 h-4 w-5/6" />
                        <Skeleton className="mt-4 h-18 w-full" />
                      </div>
                    ))}
                  </div>
                ) : requestState.recommendations ? (
                  <div className="grid gap-4">
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <div>
                        <h3 className="text-sm font-semibold text-foreground">
                          Персонализированные рекомендации
                        </h3>
                        <p className="mt-1 text-sm text-muted-foreground">
                          Найдено кандидатов:{" "}
                          {requestState.recommendations.total_candidates}
                        </p>
                      </div>
                      <Badge variant="secondary" className="gap-1.5">
                        <ShieldCheck className="size-3.5" />
                        Объяснения включены
                      </Badge>
                    </div>

                    {requestState.recommendations.recommendations.map(
                      (recommendation) => (
                        <Card key={recommendation.poi_id} className="rounded-lg">
                          <CardHeader>
                            <div className="flex flex-wrap items-start justify-between gap-3">
                              <div className="min-w-0">
                                <CardTitle className="truncate">
                                  {recommendation.rank}. {recommendation.name}
                                </CardTitle>
                                <CardDescription>
                                  {categoryLabels[recommendation.category] ??
                                    recommendation.category}
                                </CardDescription>
                              </div>
                              <Badge>{Math.round(recommendation.score * 100)} / 100</Badge>
                            </div>
                          </CardHeader>
                          <CardContent className="space-y-4">
                            <p className="text-sm leading-6 text-foreground/90">
                              {recommendation.explanation}
                            </p>

                            <div className="flex flex-wrap gap-2">
                              {recommendation.matched_interests.map((interest) => (
                                <Badge key={interest} variant="secondary">
                                  {interest}
                                </Badge>
                              ))}
                            </div>

                            <div className="grid gap-3 md:grid-cols-3">
                              <FactorLine
                                label="Интересы"
                                value={recommendation.factors.interest_match}
                              />
                              <FactorLine
                                label="Бюджет"
                                value={recommendation.factors.budget_match}
                              />
                              <FactorLine
                                label="Маршрут"
                                value={recommendation.factors.route_convenience}
                              />
                            </div>
                          </CardContent>
                        </Card>
                      ),
                    )}
                  </div>
                ) : (
                  <EmptyState
                    title="Рекомендации ещё не сформированы"
                    description="После запуска подбора здесь появится ранжированный список точек интереса с объяснениями."
                    icon={Sparkles}
                  />
                )}
              </TabsContent>

              <TabsContent value="route" className="px-4 py-4 md:px-6">
                {requestState.routePlan ? (
                  <div className="grid gap-6">
                    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                      <MetricCard
                        icon={Route}
                        label="Общая дистанция"
                        value={formatDistance(requestState.routePlan.total_distance_km)}
                        supporting={`${requestState.routePlan.route_points.length} точек`}
                      />
                      <MetricCard
                        icon={Clock3}
                        label="Время"
                        value={formatMinutes(requestState.routePlan.total_time_minutes)}
                        supporting={`переходы: ${formatMinutes(requestState.routePlan.total_travel_minutes)}`}
                      />
                      <MetricCard
                        icon={CircleDollarSign}
                        label="Бюджет"
                        value={formatRub(requestState.routePlan.estimated_budget)}
                        supporting={
                          requestState.routePlan.within_budget
                            ? "в пределах лимита"
                            : "выше лимита"
                        }
                      />
                      <MetricCard
                        icon={ShieldCheck}
                        label="Статус"
                        value={requestState.routePlan.status}
                        supporting={
                          requestState.routePlan.within_time_limit
                            ? "по времени проходит"
                            : "нужно сократить"
                        }
                      />
                    </div>

                    <div className="rounded-lg border p-4">
                      <h3 className="text-sm font-semibold text-foreground">
                        Сводка маршрута
                      </h3>
                      <p className="mt-2 text-sm leading-6 text-muted-foreground">
                        {requestState.routePlan.explanation_summary}
                      </p>
                    </div>

                    <div className="grid gap-4">
                      {requestState.routePlan.route_points.map((point) => (
                        <Card key={point.poi_id} className="rounded-lg">
                          <CardHeader>
                            <div className="flex flex-wrap items-start justify-between gap-3">
                              <div>
                                <CardTitle>
                                  {point.order}. {point.name}
                                </CardTitle>
                                <CardDescription>
                                  {point.poi.address}
                                </CardDescription>
                              </div>
                              <Badge variant="outline">
                                {categoryLabels[point.category] ?? point.category}
                              </Badge>
                            </div>
                          </CardHeader>
                          <CardContent className="grid gap-3 md:grid-cols-4">
                            <ProfileLine
                              label="Переход"
                              value={formatDistance(point.leg_distance_km)}
                            />
                            <ProfileLine
                              label="В дороге"
                              value={formatMinutes(point.leg_travel_minutes)}
                            />
                            <ProfileLine
                              label="Посещение"
                              value={formatMinutes(point.visit_minutes)}
                            />
                            <ProfileLine
                              label="Стоимость"
                              value={formatRub(point.estimated_cost_rub)}
                            />
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </div>
                ) : (
                  <EmptyState
                    title="Маршрут ещё не построен"
                    description="После подбора рекомендаций здесь появится итоговая последовательность точек, время, бюджет и дистанция."
                    icon={Route}
                  />
                )}
              </TabsContent>
            </Tabs>
          </section>
        </div>
      </main>
    </div>
  );
}

function MetricCard({
  icon: Icon,
  label,
  value,
  supporting,
}: {
  icon: typeof MapPinned;
  label: string;
  value: string;
  supporting: string;
}) {
  return (
    <div className="rounded-lg border bg-white p-4">
      <div className="flex items-center gap-2 text-muted-foreground">
        <Icon className="size-4" />
        <span className="text-xs font-medium uppercase tracking-[0.04em]">
          {label}
        </span>
      </div>
      <div className="mt-3 text-base font-semibold text-foreground">{value}</div>
      <div className="mt-1 text-sm text-muted-foreground">{supporting}</div>
    </div>
  );
}

function ProfileLine({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-3 text-sm">
      <span className="text-muted-foreground">{label}</span>
      <span className="text-right font-medium text-foreground">{value}</span>
    </div>
  );
}

function FactorLine({ label, value }: { label: string; value: number }) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between gap-3 text-xs text-muted-foreground">
        <span>{label}</span>
        <span>{Math.round(value * 100)}%</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-muted">
        <div
          className="h-full rounded-full bg-primary"
          style={{ width: `${Math.max(8, Math.round(value * 100))}%` }}
        />
      </div>
    </div>
  );
}

function EmptyState({
  title,
  description,
  icon: Icon,
}: {
  title: string;
  description: string;
  icon: typeof Sparkles;
}) {
  return (
    <div className="flex min-h-[420px] flex-col items-center justify-center rounded-lg border border-dashed bg-muted/20 px-6 text-center">
      <div className="flex size-11 items-center justify-center rounded-lg bg-primary/10 text-primary">
        <Icon className="size-5" />
      </div>
      <h3 className="mt-4 text-base font-semibold text-foreground">{title}</h3>
      <p className="mt-2 max-w-lg text-sm leading-6 text-muted-foreground">
        {description}
      </p>
    </div>
  );
}

function CityCard({
  city,
  isActive,
  onSelect,
}: {
  city: City;
  isActive: boolean;
  onSelect: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onSelect}
      className={`w-full rounded-lg border p-3 text-left transition-colors ${
        isActive
          ? "border-primary/30 bg-primary/6"
          : "border-border bg-white hover:bg-muted/40"
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="truncate font-medium text-foreground">{city.name}</div>
          <div className="mt-1 text-sm text-muted-foreground">{city.region}</div>
        </div>
        <Badge variant={isActive ? "default" : "outline"}>{city.pois_count} POI</Badge>
      </div>
      <div className="mt-3 flex items-center justify-between gap-3 text-xs text-muted-foreground">
        <span>{formatPopulation(city.population)} чел.</span>
        <span>
          {city.latitude.toFixed(2)}, {city.longitude.toFixed(2)}
        </span>
      </div>
    </button>
  );
}
