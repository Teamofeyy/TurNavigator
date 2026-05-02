// City types
export interface City {
  id: number
  name: string
  region: string
  country: string
  latitude: number
  longitude: number
  population: number
  source: string
  external_id: string
  wikidata_id: string | null
  osm_id: number | null
  pois_count: number
}

// Profile and Trip Request types
export type CompromiseStrategy = 'balanced' | 'budget_first' | 'time_first' | 'experience_first'
export type TrustLevel = 'low' | 'medium' | 'high'
export type PreferredTimeWindow = 'morning' | 'afternoon' | 'evening'

export interface TripProfile {
  profile_name: string
  interests: string[]
  budget_level: 'low' | 'medium' | 'high'
  max_budget: number
  pace: 'relaxed' | 'moderate' | 'intensive'
  max_walking_distance_km: number
  preferred_transport: 'walking' | 'public_transport' | 'car' | 'mixed'
  explanation_level: 'short' | 'detailed'
  goals: string[]
  must_have: string[]
  avoid: string[]
  compromise_strategy: CompromiseStrategy
  trust_level: TrustLevel
  accessibility_needs: string[]
  preferred_time_windows: PreferredTimeWindow[]
}

export interface SavedProfile extends TripProfile {
  id: number
  created_at: string
  updated_at: string
}

export interface TripLocation {
  address: string
  latitude: number
  longitude: number
  name?: string | null
  poi_id?: number | null
}

export interface TripConstraints {
  include_accommodation: boolean
  return_to_start: boolean
}

export interface TripRequestInput {
  city_id: number
  profile_id?: number | null
  profile?: TripProfile | null
  days_count: number
  daily_time_limit_hours: number
  selected_interests: string[]
  constraints: TripConstraints
  start_location?: TripLocation | null
  end_location?: TripLocation | null
}

export interface TripRequest {
  id: number
  city_id: number
  profile_id: number
  profile: SavedProfile
  days_count: number
  daily_time_limit_hours: number
  selected_interests: string[] | null
  constraints: TripConstraints
  start_location: TripLocation | null
  end_location: TripLocation | null
  created_at: string
}

// POI types
export interface POIImage {
  provider: string
  original_url: string | null
  thumbnail_url: string | null
  source_page_url: string | null
  license: string | null
  author: string | null
  attribution_text: string | null
  width: number | null
  height: number | null
  is_primary: boolean
}

export interface POISourceLink {
  provider: string
  external_id: string
  url: string | null
  license: string | null
  last_synced_at: string | null
}

export interface POI {
  id: number
  city_id: number
  name: string
  category: string
  subcategory: string
  latitude: number
  longitude: number
  address: string
  description: string
  opening_hours: string | null
  website: string | null
  phone: string | null
  source: string
  external_id: string
  wikidata_id: string | null
  wikipedia_title: string | null
  wikipedia_url: string | null
  wikimedia_commons: string | null
  osm_tags: Record<string, string>
  estimated_price_level: string
  average_cost_rub: number
  estimated_visit_minutes: number
  popularity_score: number
  data_quality_score: number
  interests: string[]
  interest_source: string
  primary_image: POIImage | null
  images: POIImage[]
  source_links: POISourceLink[]
  data_freshness_days: number
  last_enriched_at: string | null
}

// Recommendation types
export interface RecommendationFactors {
  interest_match: number
  budget_match: number
  route_convenience: number
  pace_match: number
  popularity_score: number
  data_quality_score: number
}

export interface ConstraintStatus {
  budget: string
  pace: string
  distance: string
}

export interface Recommendation {
  poi_id: number
  name: string
  category: string
  score: number
  rank: number
  matched_interests: string[]
  factors: RecommendationFactors
  constraint_status: ConstraintStatus
  explanation: string
  poi: POI
}

export interface RecommendationsResponse {
  recommendation_run_id: number
  trip_request_id: number
  city_id: number
  total_candidates: number
  recommendations: Recommendation[]
}

export interface GenerateRecommendationsInput {
  trip_request_id: number
  limit: number
  include_accommodation: boolean
  include_categories: string[] | null
  exclude_categories: string[]
}

// Route types
export interface RoutePoint {
  order: number
  poi_id: number
  name: string
  category: string
  latitude: number
  longitude: number
  leg_distance_km: number
  leg_travel_minutes: number
  visit_minutes: number
  estimated_cost_rub: number
  cumulative_distance_km: number
  cumulative_time_minutes: number
  cumulative_budget_rub: number
  poi: POI
}

export interface Route {
  id: number
  trip_request_id: number
  city_id: number
  status: string
  total_distance_km: number
  total_travel_minutes: number
  total_visit_minutes: number
  total_time_minutes: number
  estimated_budget: number
  days_count: number
  daily_time_limit_minutes: number
  within_time_limit: boolean
  within_budget: boolean
  start_location: TripLocation | null
  end_location: TripLocation | null
  return_leg_distance_km: number
  return_leg_travel_minutes: number
  skipped_poi_ids: number[]
  route_points: RoutePoint[]
  explanation_summary: string
}

export interface BuildRouteInput {
  trip_request_id: number
  poi_ids?: number[] | null
  max_points: number
  optimize_order: boolean
  strict_constraints: boolean
  start_location?: TripLocation | null
  end_location?: TripLocation | null
}

export interface FeedbackInput {
  route_id: number
  rating: number
  comment?: string | null
}

export interface FeedbackResponse {
  id: number
  route_id: number
  trip_request_id: number
  city_id: number
  rating: number
  comment: string | null
  route_points_count: number
  estimated_budget: number
  total_time_minutes: number
  created_at: string
}

// UI State types
export type TabType = 'context' | 'recommendations' | 'route'

export interface PlanningState {
  selectedCity: City | null
  selectedHotel: POI | null
  selectedProfileId: number | null
  profileName: string
  hotelAddress: string
  interests: string[]
  goals: string[]
  mustHave: string
  avoid: string
  budgetLevel: 'low' | 'medium' | 'high'
  maxBudget: number
  pace: 'relaxed' | 'moderate' | 'intensive'
  maxWalkingDistance: number
  preferredTransport: 'walking' | 'public_transport' | 'car' | 'mixed'
  explanationLevel: 'short' | 'detailed'
  compromiseStrategy: CompromiseStrategy
  trustLevel: TrustLevel
  accessibilityNeeds: string[]
  preferredTimeWindows: PreferredTimeWindow[]
  daysCount: number
  dailyTimeLimit: number
}

// Interest options
export const INTERESTS = [
  { id: 'history', label: 'История', icon: 'landmark' },
  { id: 'culture', label: 'Культура', icon: 'palette' },
  { id: 'food', label: 'Еда', icon: 'utensils' },
  { id: 'nature', label: 'Природа', icon: 'trees' },
  { id: 'architecture', label: 'Архитектура', icon: 'building' },
  { id: 'entertainment', label: 'Развлечения', icon: 'party-popper' },
  { id: 'shopping', label: 'Шопинг', icon: 'shopping-bag' },
  { id: 'nightlife', label: 'Ночная жизнь', icon: 'moon' },
] as const

export const PROFILE_GOALS = [
  { id: 'discover_local_culture', label: 'Локальная культура' },
  { id: 'optimize_budget', label: 'Экономить бюджет' },
  { id: 'minimize_transfers', label: 'Меньше пересадок' },
  { id: 'maximize_variety', label: 'Больше разнообразия' },
  { id: 'photo_spots', label: 'Фототочки' },
] as const

export const ACCESSIBILITY_OPTIONS = [
  { id: 'wheelchair_access', label: 'Безбарьерная среда' },
  { id: 'quiet_places', label: 'Тихие места' },
  { id: 'family_friendly', label: 'С детьми удобно' },
  { id: 'rest_breaks', label: 'Нужны паузы на отдых' },
] as const

export const TIME_WINDOW_OPTIONS = [
  { id: 'morning' as const, label: 'Утро' },
  { id: 'afternoon' as const, label: 'День' },
  { id: 'evening' as const, label: 'Вечер' },
] as const

// Category labels
export const CATEGORY_LABELS: Record<string, string> = {
  culture: 'Культура',
  history: 'История',
  food: 'Еда',
  nature: 'Природа',
  architecture: 'Архитектура',
  entertainment: 'Развлечения',
  shopping: 'Шопинг',
  nightlife: 'Ночная жизнь',
  museum: 'Музей',
  park: 'Парк',
  restaurant: 'Ресторан',
  cafe: 'Кафе',
  confectionery_cafe: 'Кондитерская',
  fast_food: 'Фастфуд',
  food_court: 'Фуд-корт',
  bakery: 'Пекарня',
  confectionery: 'Кондитерская',
  bar: 'Бар',
  pub: 'Паб',
  biergarten: 'Пивной сад',
  nightclub: 'Клуб',
  mall: 'Торговый центр',
  department_store: 'Универмаг',
  gift_shop: 'Подарки',
  souvenir_shop: 'Сувениры',
  clothes_store: 'Одежда',
  bookstore: 'Книжный',
}

export function getCategoryLabel(category: string): string {
  return CATEGORY_LABELS[category] || category
}
