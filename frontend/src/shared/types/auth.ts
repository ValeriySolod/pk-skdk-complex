export type AuthUser = {
  id: number;
  username: string;
  fullName: string;
  role: string;
  department?: string | null;
  isActive: boolean;
};

export type AuthToken = {
  accessToken: string;
  tokenType: 'bearer';
};

export type AuthSession = {
  user: AuthUser;
  token: AuthToken;
};
