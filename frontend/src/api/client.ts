export class ApiError extends Error {
  constructor(public status: number, public code: string, message: string, public trace_id?: string) {
    super(message);
    this.name = 'ApiError';
  }
}

let accessToken = "dummy-token"; // Assume injected via initial HTML payload or secure cookie

// Note: A real app would regenerate these types from the OpenAPI schema using openapi-typescript
// Here we stub the interfaces strictly to match the prompt's backend payloads.

export interface TrendPoint {
  timestamp: string;
  total_executions: number;
  total_failures: number;
  failure_rate: number;
}

export interface FlakyEntry {
  test_case_id: string;
  test_case_name: string;
  flaky_score: number;
  flip_count: number;
}

export async function fetchWithAuth<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set('Authorization', `Bearer ${accessToken}`);
  headers.set('Content-Type', 'application/json');

  let response = await fetch(endpoint, { ...options, headers });

  // 401 -> refresh token -> retry once
  if (response.status === 401) {
    console.warn("401 detected, attempting token refresh...");
    // Mock refresh logic
    accessToken = "refreshed-dummy-token";
    headers.set('Authorization', `Bearer ${accessToken}`);
    
    response = await fetch(endpoint, { ...options, headers });
    if (response.status === 401) {
      window.location.href = '/login'; // Redirect to login on repeated failure
      throw new Error("Session expired");
    }
  }

  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch {
      errorData = { error: { message: response.statusText, code: "UNKNOWN" }};
    }
    throw new ApiError(
      response.status, 
      errorData.error?.code || "UNKNOWN", 
      errorData.error?.message || "An unexpected error occurred",
      errorData.error?.trace_id
    );
  }

  return response.json();
}

// Stubs for useQuery
export const api = {
  dashboard: {
    getTrends: (repoId: string) => fetchWithAuth<{data_points: TrendPoint[]}>(`/api/v1/analytics/trends/failures?repository_id=${repoId}&from=2023-01-01&to=2023-12-31&granularity=day`),
    getFlaky: (repoId: string) => fetchWithAuth<FlakyEntry[]>(`/api/v1/analytics/leaderboard/flaky-tests?repository_id=${repoId}&limit=5`)
  }
}
