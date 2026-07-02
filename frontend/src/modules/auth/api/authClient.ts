import type { AuthSession, AuthUser } from '../../../shared/types/auth';

export type LoginCredentials = {
  username: string;
  password: string;
};

export type AuthApi = {
  login(credentials: LoginCredentials): Promise<AuthSession>;
  getCurrentUser(): Promise<AuthUser>;
  logout(): Promise<void>;
};
