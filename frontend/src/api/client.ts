export const AUTH_TOKEN_STORAGE_KEY = 'pk_skdk_token';
export const getToken = (): string | null => localStorage.getItem(AUTH_TOKEN_STORAGE_KEY);
export const setToken = (token: string): void => localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, token);
export const removeToken = (): void => localStorage.removeItem(AUTH_TOKEN_STORAGE_KEY);

export class ApiError extends Error {
  readonly kind: 'http' | 'network';
  readonly status?: number;
  readonly detail?: unknown;

  constructor(message: string, kind: 'http' | 'network', status?: number, detail?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.kind = kind;
    this.status = status;
    this.detail = detail;
  }
}

const API_CONFIGURATION_ERROR_MESSAGE =
  'VITE_API_URL must be an absolute HTTP(S) URL ending at /api/v1, without credentials, query, or fragment.';

export class ApiConfigurationError extends Error {
  constructor() {
    super(API_CONFIGURATION_ERROR_MESSAGE);
    this.name = 'ApiConfigurationError';
  }
}

export type ApiEnvironment = Record<string, string | boolean | undefined>;
export function resolveApiBaseUrl(environment: ApiEnvironment | undefined): string {
  const value = environment?.VITE_API_URL;
  if (typeof value !== 'string' || value.trim() === '') throw new ApiConfigurationError();
  let url: URL;
  try { url = new URL(value); } catch { throw new ApiConfigurationError(); }
  const normalizedPath = url.pathname.replace(/\/$/, '');
  if (
    !['http:', 'https:'].includes(url.protocol) ||
    url.username !== '' ||
    url.password !== '' ||
    url.search !== '' ||
    url.hash !== '' ||
    normalizedPath !== '/api/v1'
  ) throw new ApiConfigurationError();
  url.pathname = normalizedPath;
  return url.toString().replace(/\/$/, '');
}
const getApiBaseUrl = (): string => resolveApiBaseUrl(import.meta.env);

type RequestDependencies = { baseUrl?: string; fetch?: typeof fetch; token?: () => string | null };

export async function apiRequest<T>(path: string, options: RequestInit = {}, dependencies: RequestDependencies = {}): Promise<T> {
  const token = (dependencies.token ?? getToken)();
  const baseUrl = dependencies.baseUrl === undefined
    ? getApiBaseUrl()
    : resolveApiBaseUrl({ VITE_API_URL: dependencies.baseUrl });
  let response: Response;
  try {
    response = await (dependencies.fetch ?? fetch)(`${baseUrl}${path}`, {
      ...options,
      headers: {
        Accept: 'application/json',
        ...(options.body ? { 'Content-Type': 'application/json' } : {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
      },
    });
  } catch {
    throw new ApiError('The backend could not be reached.', 'network');
  }
  if (!response.ok) {
    let detail: unknown;
    try {
      const payload: unknown = await response.json();
      detail = typeof payload === 'object' && payload !== null && 'detail' in payload ? (payload as { detail: unknown }).detail : payload;
    } catch { detail = undefined; }
    throw new ApiError(`Backend request failed with status ${response.status}.`, 'http', response.status, detail);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}
