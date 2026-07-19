import { IS_DEMO_MODE } from '../shared/config.ts';
import { apiRequest, setToken, removeToken } from './client.ts';
import { InvalidUserResponseError, parseUser, type User } from './userContract.ts';
export { InvalidUserResponseError, parseUser, type User } from './userContract.ts';

export interface LoginResponse {
  access_token: string;
  token_type: string;
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

  try {
    return parseUser(await apiRequest<unknown>('/auth/me'));
  } catch (error: unknown) {
    if (error instanceof SyntaxError) throw new InvalidUserResponseError();
    throw error;
  }
}

export function logout(): void {
  removeToken();
}
