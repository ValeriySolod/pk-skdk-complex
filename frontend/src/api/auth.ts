import { IS_DEMO_MODE } from '../shared/config';
import { apiRequest, setToken, removeToken } from './client';

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: number;
  username: string;
  full_name: string;
  role: string;
  department: string | null;
  is_active: boolean;
}

export async function login(
  username: string,
  password: string
): Promise<void> {
  if (IS_DEMO_MODE) {
    if (username === 'admin' && password === 'admin12345') {
      setToken('demo-token');
      return;
    }

    throw new Error('Невірний логін або пароль');
  }

  const formData = new URLSearchParams();

  formData.append('username', username);
  formData.append('password', password);

  const data = await apiRequest<LoginResponse>('/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData,
  }, { token: () => null });

  setToken(data.access_token);
}

export async function getMe(): Promise<User> {
  if (IS_DEMO_MODE) {
    return {
      id: 1,
      username: 'admin',
      full_name: 'Demo Admin',
      role: 'SYSTEM_ADMIN',
      department: null,
      is_active: true,
    };
  }

  return apiRequest<User>('/auth/me');
}

export function logout(): void {
  removeToken();
}
