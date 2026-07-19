export interface User {
  id: number;
  username: string;
  full_name: string;
  role: string;
  department: string | null;
  is_active: boolean;
}

export class InvalidUserResponseError extends Error {
  constructor() {
    super('The current-user response does not match the UserRead contract.');
    this.name = 'InvalidUserResponseError';
  }
}

export function parseUser(value: unknown): User {
  if (typeof value !== 'object' || value === null) throw new InvalidUserResponseError();
  const user = value as Record<string, unknown>;
  if (
    !Number.isInteger(user.id) ||
    typeof user.username !== 'string' ||
    typeof user.full_name !== 'string' ||
    typeof user.role !== 'string' ||
    (typeof user.department !== 'string' && user.department !== null) ||
    typeof user.is_active !== 'boolean'
  ) throw new InvalidUserResponseError();

  return {
    id: user.id as number,
    username: user.username,
    full_name: user.full_name,
    role: user.role,
    department: user.department,
    is_active: user.is_active,
  };
}
