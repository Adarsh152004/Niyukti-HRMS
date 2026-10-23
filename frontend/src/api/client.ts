import { ApiError } from './errors';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export interface RequestOptions extends RequestInit {
  params?: Record<string, string | number | boolean | undefined>;
}

export async function apiClient<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { params, headers, ...customConfig } = options;

  let url = `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;

  if (params) {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        searchParams.append(key, String(value));
      }
    });
    const queryString = searchParams.toString();
    if (queryString) {
      url += `?${queryString}`;
    }
  }

  const defaultHeaders: HeadersInit = {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  };

  const config: RequestInit = {
    ...customConfig,
    headers: {
      ...defaultHeaders,
      ...headers,
    },
  };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      let errorMessage = `HTTP Error ${response.status}: ${response.statusText}`;
      let errorCode = 'HTTP_ERROR';
      let details: Record<string, unknown> | undefined;
      let correlationId: string | undefined;

      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
        errorCode = errorData.code || errorCode;
        details = errorData.details;
        correlationId = errorData.correlation_id || response.headers.get('x-correlation-id') || undefined;
      } catch {
        // Response was not JSON
      }

      throw new ApiError(response.status, errorMessage, errorCode, details, correlationId);
    }

    if (response.status === 204) {
      return {} as T;
    }

    return await response.json();
  } catch (err) {
    if (err instanceof ApiError) {
      throw err;
    }
    throw new ApiError(0, err instanceof Error ? err.message : 'Network connection failed', 'NETWORK_ERROR');
  }
}
