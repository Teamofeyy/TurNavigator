import {
  City,
  PointOfInterest,
  RecommendationGenerateRequest,
  RecommendationListResponse,
  RouteBuildRequest,
  RoutePlanResponse,
  TripRequestCreate,
  TripRequestResponse,
} from "@/lib/types";
import { requestBackend } from "@/lib/backend-api";

async function parseJsonResponse<T>(response: Response): Promise<T> {
  const data = (await response.json()) as T | { detail?: string };

  if (!response.ok) {
    const detail =
      typeof data === "object" && data !== null && "detail" in data
        ? data.detail
        : undefined;
    throw new Error(detail ?? "Backend request failed.");
  }

  return data as T;
}

export async function listCities(): Promise<City[]> {
  const response = await requestBackend("/cities");
  return parseJsonResponse<City[]>(response);
}

export async function listCityPois(
  cityId: number,
  query?: URLSearchParams,
): Promise<PointOfInterest[]> {
  const search = query && query.toString() ? `?${query.toString()}` : "";
  const response = await requestBackend(`/cities/${cityId}/pois${search}`);
  return parseJsonResponse<PointOfInterest[]>(response);
}

export async function createTripRequest(
  payload: TripRequestCreate,
): Promise<TripRequestResponse> {
  const response = await requestBackend("/trip-requests", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  return parseJsonResponse<TripRequestResponse>(response);
}

export async function generateRecommendations(
  payload: RecommendationGenerateRequest,
): Promise<RecommendationListResponse> {
  const response = await requestBackend("/recommendations/generate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  return parseJsonResponse<RecommendationListResponse>(response);
}

export async function buildRoutePlan(
  payload: RouteBuildRequest,
): Promise<RoutePlanResponse> {
  const response = await requestBackend("/routes/build", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  return parseJsonResponse<RoutePlanResponse>(response);
}
