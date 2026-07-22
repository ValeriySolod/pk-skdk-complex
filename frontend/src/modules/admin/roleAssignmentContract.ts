export interface UserManagementRoleAssignmentRead {
  id: number;
  user_id: number;
  role_code: string;
  scope_type: string | null;
  scope_id: number | null;
  is_active: boolean;
  assigned_by_user_id: number | null;
  assigned_at: string;
  revoked_at: string | null;
}

export class InvalidRoleAssignmentsResponseError extends Error {
  constructor() {
    super('The role assignments response does not match the UserManagementRoleAssignmentRead contract.');
    this.name = 'InvalidRoleAssignmentsResponseError';
  }
}

const contractKeys = ['assigned_at', 'assigned_by_user_id', 'id', 'is_active', 'revoked_at', 'role_code', 'scope_id', 'scope_type', 'user_id'];
const dateTimePattern = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d+)?(?:Z|([+-])(\d{2}):(\d{2}))?$/;

function isValidDateTime(value: unknown): value is string {
  if (typeof value !== 'string') return false;
  const match = dateTimePattern.exec(value);
  if (match === null) return false;
  const [, year, month, day, hour, minute, second, , offsetHour, offsetMinute] = match;
  const [y, m, d, h, min, s] = [year, month, day, hour, minute, second].map(Number);
  if (h > 23 || min > 59 || s > 59 || Number(offsetHour ?? 0) > 23 || Number(offsetMinute ?? 0) > 59) return false;
  const date = new Date(Date.UTC(y, m - 1, d, h, min, s));
  return date.getUTCFullYear() === y && date.getUTCMonth() === m - 1 && date.getUTCDate() === d;
}

function isNullableInteger(value: unknown): value is number | null { return value === null || Number.isInteger(value); }
function isNullableString(value: unknown): value is string | null { return value === null || typeof value === 'string'; }

function parseRoleAssignment(value: unknown): UserManagementRoleAssignmentRead {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) throw new InvalidRoleAssignmentsResponseError();
  const assignment = value as Record<string, unknown>;
  const keys = Object.keys(assignment).sort();
  if (
    keys.length !== contractKeys.length || keys.some((key, index) => key !== contractKeys[index]) ||
    !Number.isInteger(assignment.id) || !Number.isInteger(assignment.user_id) || typeof assignment.role_code !== 'string' ||
    !isNullableString(assignment.scope_type) || !isNullableInteger(assignment.scope_id) || typeof assignment.is_active !== 'boolean' ||
    !isNullableInteger(assignment.assigned_by_user_id) || !isValidDateTime(assignment.assigned_at) ||
    !(assignment.revoked_at === null || isValidDateTime(assignment.revoked_at))
  ) throw new InvalidRoleAssignmentsResponseError();
  return assignment as unknown as UserManagementRoleAssignmentRead;
}

export function parseRoleAssignments(value: unknown): UserManagementRoleAssignmentRead[] {
  if (!Array.isArray(value)) throw new InvalidRoleAssignmentsResponseError();
  return value.map(parseRoleAssignment);
}
