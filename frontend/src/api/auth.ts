
import { IS_DEMO_MODE } from '../shared/config';
import { setToken, removeToken } from './client';

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: number;
  username: string;
  full_name: string;
  role: string;
  department?: string;
  is_active?: boolean;
}

export async function login(username: string, password: string): Promise<void> {
  if (IS_DEMO_MODE) {
    if (username === 'admin' && password === 'admin12345') {
      setToken('demo-token');
      return;
    }

    throw new Error('Invalid demo credentials');
  }

  const formData = new URLSearchParams();

  formData.append('username', username);
  formData.append('password', password);

  const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

  const response = await fetch(`${API_URL}/api/v1/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Invalid username or password');
  }

  const data = (await response.json()) as LoginResponse;
  setToken(data.access_token);
}

export function logout(): void {
  removeToken();
}

export function getCurrentUser(): User | null {
  if (IS_DEMO_MODE) {
    return {
      id: 1,
      username: 'admin',
      full_name: 'Demo Admin',
      role: 'SYSTEM_ADMIN',
      department: 'Демо',
      is_active: true,
    };
  }

  return null;
}import { apiRequest, setToken, removeToken } from './client';

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: number;
  username: string;
  full_name: string;
  role: string;
  department?: string;
  is_active?: boolean;
}

export async function login(username: string, password: string): Promise<void> {
  const formData = new URLSearchParams();

  formData.append('username', username);
  formData.append('password', password);

  const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

  const response = await fetch(`${API_URL}/api/v1/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Невірний логін або пароль');
  }

  const data = (await response.json()) as LoginResponse;

  setToken(data.access_token);
}

export async function getMe(): Promise<User> {
  return apiRequest<User>('/api/v1/auth/me');
}

export function logout(): void {
  removeToken();
}