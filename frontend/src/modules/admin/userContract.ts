export interface UserManagementUserRead {
  id: number;
  username: string;
  email: string | null;
  is_active: boolean;
}

export class InvalidUsersResponseError extends Error {
  constructor() {
    super('The users response does not match the UserRead contract.');
    this.name = 'InvalidUsersResponseError';
  }
}

const contractKeys = ['email', 'id', 'is_active', 'username'];

function parseUser(value: unknown): UserManagementUserRead {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) {
    throw new InvalidUsersResponseError();
  }
  const user = value as Record<string, unknown>;
  const keys = Object.keys(user).sort();
  if (
    keys.length !== contractKeys.length ||
    keys.some((key, index) => key !== contractKeys[index]) ||
    !Number.isInteger(user.id) ||
    typeof user.username !== 'string' ||
    !(user.email === null || typeof user.email === 'string') ||
    typeof user.is_active !== 'boolean'
  ) {
    throw new InvalidUsersResponseError();
  }
  return user as unknown as UserManagementUserRead;
}

export function parseUsers(value: unknown): UserManagementUserRead[] {
  if (!Array.isArray(value)) throw new InvalidUsersResponseError();
  return value.map(parseUser);
}
