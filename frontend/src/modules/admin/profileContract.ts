export interface UserManagementProfileRead {
  id: number;
  user_id: number;
  display_name: string | null;
  personnel_number: string | null;
  job_title: string | null;
  phone_number: string | null;
  is_active: boolean;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export class InvalidProfilesResponseError extends Error {
  constructor() {
    super('The profiles response does not match the UserManagementProfileRead contract.');
    this.name = 'InvalidProfilesResponseError';
  }
}

const contractKeys = ['created_at', 'display_name', 'id', 'is_active', 'job_title', 'notes', 'personnel_number', 'phone_number', 'updated_at', 'user_id'];
const dateTimePattern = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d+)?(?:Z|([+-])(\d{2}):(\d{2}))?$/;

function isValidDateTime(value: unknown): value is string {
  if (typeof value !== 'string') return false;
  const match = dateTimePattern.exec(value);
  if (match === null) return false;
  const [, year, month, day, hour, minute, second, , offsetHour, offsetMinute] = match;
  const numeric = [year, month, day, hour, minute, second].map(Number);
  const [y, m, d, h, min, s] = numeric;
  if (h > 23 || min > 59 || s > 59 || Number(offsetHour ?? 0) > 23 || Number(offsetMinute ?? 0) > 59) return false;
  const date = new Date(Date.UTC(y, m - 1, d, h, min, s));
  return date.getUTCFullYear() === y && date.getUTCMonth() === m - 1 && date.getUTCDate() === d;
}

function isNullableString(value: unknown): value is string | null {
  return value === null || typeof value === 'string';
}

function parseProfile(value: unknown): UserManagementProfileRead {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) throw new InvalidProfilesResponseError();
  const profile = value as Record<string, unknown>;
  const keys = Object.keys(profile).sort();
  if (
    keys.length !== contractKeys.length || keys.some((key, index) => key !== contractKeys[index]) ||
    !Number.isInteger(profile.id) || !Number.isInteger(profile.user_id) ||
    !isNullableString(profile.display_name) || !isNullableString(profile.personnel_number) ||
    !isNullableString(profile.job_title) || !isNullableString(profile.phone_number) ||
    typeof profile.is_active !== 'boolean' || !isNullableString(profile.notes) ||
    !isValidDateTime(profile.created_at) || !isValidDateTime(profile.updated_at)
  ) throw new InvalidProfilesResponseError();
  return profile as unknown as UserManagementProfileRead;
}

export function parseProfiles(value: unknown): UserManagementProfileRead[] {
  if (!Array.isArray(value)) throw new InvalidProfilesResponseError();
  return value.map(parseProfile);
}
