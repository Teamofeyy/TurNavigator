import type {
  City,
  TripRequest,
  TripRequestInput,
  SavedProfile,
  TripProfile,
  RecommendationsResponse,
  GenerateRecommendationsInput,
  Route,
  BuildRouteInput,
  FeedbackInput,
  FeedbackResponse,
  POI,
} from './types'

class ApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

async function fetchApi<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  })

  if (!response.ok) {
    let message = `HTTP error ${response.status}`

    try {
      const data = (await response.json()) as { detail?: string; error?: string }
      message = data.detail ?? data.error ?? message
    } catch {
      const errorText = await response.text()
      if (errorText) {
        message = errorText
      }
    }

    throw new ApiError(response.status, message)
  }

  return response.json()
}

export const api = {
  // Cities
  async getCities(): Promise<City[]> {
    return fetchApi<City[]>('/api/cities')
  },

  async getCityPois(
    cityId: number,
    options?: { category?: string; limit?: number; offset?: number }
  ): Promise<POI[]> {
    const params = new URLSearchParams()
    if (options?.category) {
      params.set('category', options.category)
    }
    if (typeof options?.limit === 'number') {
      params.set('limit', String(options.limit))
    }
    if (typeof options?.offset === 'number') {
      params.set('offset', String(options.offset))
    }

    const query = params.size > 0 ? `?${params.toString()}` : ''
    return fetchApi<POI[]>(`/api/cities/${cityId}/pois${query}`)
  },

  // Profiles
  async createProfile(input: TripProfile): Promise<SavedProfile> {
    return fetchApi<SavedProfile>('/api/profiles', {
      method: 'POST',
      body: JSON.stringify(input),
    })
  },

  // Trip Requests
  async createTripRequest(input: TripRequestInput): Promise<TripRequest> {
    return fetchApi<TripRequest>('/api/trip-requests', {
      method: 'POST',
      body: JSON.stringify(input),
    })
  },

  // Recommendations
  async generateRecommendations(input: GenerateRecommendationsInput): Promise<RecommendationsResponse> {
    return fetchApi<RecommendationsResponse>('/api/recommendations/generate', {
      method: 'POST',
      body: JSON.stringify(input),
    })
  },

  // Routes
  async buildRoute(input: BuildRouteInput): Promise<Route> {
    return fetchApi<Route>('/api/routes/build', {
      method: 'POST',
      body: JSON.stringify(input),
    })
  },

  // Feedback
  async submitFeedback(input: FeedbackInput): Promise<FeedbackResponse> {
    return fetchApi<FeedbackResponse>('/api/feedback', {
      method: 'POST',
      body: JSON.stringify(input),
    })
  },
}

export { ApiError }
