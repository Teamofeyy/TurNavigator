import type {
  City,
  TripRequest,
  TripRequestInput,
  RecommendationsResponse,
  GenerateRecommendationsInput,
  Route,
  BuildRouteInput,
  FeedbackInput,
  FeedbackResponse,
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
