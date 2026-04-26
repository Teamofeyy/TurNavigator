export type BudgetLevel = "low" | "medium" | "high";
export type Pace = "relaxed" | "moderate" | "intensive";
export type Transport = "walking" | "public_transport" | "car" | "mixed";
export type ExplanationLevel = "short" | "detailed";
export type RouteStatus = "built" | "partially_built" | "empty";

export interface City {
  id: number;
  name: string;
  region: string;
  country: string;
  latitude: number;
  longitude: number;
  population: number;
  source: string;
  external_id: string;
  wikidata_id: string | null;
  osm_id: number | null;
  pois_count: number;
}

export interface PointOfInterest {
  id: number;
  city_id: number;
  name: string;
  category: string;
  subcategory: string;
  latitude: number;
  longitude: number;
  address: string;
  description: string;
  opening_hours: string | null;
  website: string | null;
  phone: string | null;
  source: string;
  external_id: string;
  wikidata_id: string | null;
  osm_tags: Record<string, string>;
  estimated_price_level: string;
  average_cost_rub: number;
  estimated_visit_minutes: number;
  popularity_score: number;
  data_quality_score: number;
  interests: string[];
}

export interface UserProfileInput {
  interests: string[];
  budget_level: BudgetLevel;
  max_budget: number;
  pace: Pace;
  max_walking_distance_km: number;
  preferred_transport: Transport;
  explanation_level: ExplanationLevel;
}

export interface TripRequestCreate {
  city_id: number;
  profile: UserProfileInput;
  days_count: number;
  daily_time_limit_hours: number;
  selected_interests: string[] | null;
  constraints: Record<string, string | number | boolean>;
}

export interface TripRequestResponse extends TripRequestCreate {
  id: number;
  created_at: string;
}

export interface RecommendationGenerateRequest {
  trip_request_id: number;
  limit: number;
  include_accommodation: boolean;
  include_categories: string[] | null;
  exclude_categories: string[];
}

export interface RecommendationFactors {
  interest_match: number;
  budget_match: number;
  route_convenience: number;
  pace_match: number;
  popularity_score: number;
  data_quality_score: number;
}

export interface ConstraintStatus {
  budget: string;
  pace: string;
  distance: string;
}

export interface Recommendation {
  poi_id: number;
  name: string;
  category: string;
  score: number;
  rank: number;
  matched_interests: string[];
  factors: RecommendationFactors;
  constraint_status: ConstraintStatus;
  explanation: string;
  poi: PointOfInterest;
}

export interface RecommendationListResponse {
  trip_request_id: number;
  city_id: number;
  total_candidates: number;
  recommendations: Recommendation[];
}

export interface RouteBuildRequest {
  trip_request_id: number;
  poi_ids?: number[] | null;
  max_points: number;
  optimize_order: boolean;
  strict_constraints: boolean;
}

export interface RoutePoint {
  order: number;
  poi_id: number;
  name: string;
  category: string;
  latitude: number;
  longitude: number;
  leg_distance_km: number;
  leg_travel_minutes: number;
  visit_minutes: number;
  estimated_cost_rub: number;
  cumulative_distance_km: number;
  cumulative_time_minutes: number;
  cumulative_budget_rub: number;
  poi: PointOfInterest;
}

export interface RoutePlanResponse {
  id: number;
  trip_request_id: number;
  city_id: number;
  status: RouteStatus;
  total_distance_km: number;
  total_travel_minutes: number;
  total_visit_minutes: number;
  total_time_minutes: number;
  estimated_budget: number;
  days_count: number;
  daily_time_limit_minutes: number;
  within_time_limit: boolean;
  within_budget: boolean;
  skipped_poi_ids: number[];
  route_points: RoutePoint[];
  explanation_summary: string;
}

export interface ApiError {
  detail?: string;
}
