export const AUTH_TOKEN_STORAGE_KEY = 'pk_skdk_token';

export type TokenStorage = {
  getAccessToken(): string | null;
  setAccessToken(token: string): void;
  clear(): void;
};
