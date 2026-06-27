const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export function getToken(): string | null {
  return localStorage.getItem('pk_skdk_token');
}

export function setToken(token: string): void {
  localStorage.setItem('pk_skdk_token', token);
}

export function removeToken(): void {
  localStorage.removeItem('pk_skdk_token');
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json() as Promise<T>;
}