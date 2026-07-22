export interface UserManagementAuditEventRead {
  id: number;
  actor_user_id: number | null;
  target_user_id: number | null;
  event_type: string;
  summary: string | null;
  details: Record<string, unknown> | null;
  created_at: string;
}

export class InvalidAuditEventsResponseError extends Error {
  constructor() {
    super('The audit events response does not match the UserManagementAuditEventRead contract.');
    this.name = 'InvalidAuditEventsResponseError';
  }
}

const contractKeys = ['actor_user_id', 'created_at', 'details', 'event_type', 'id', 'summary', 'target_user_id'];
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
function isNullablePlainObject(value: unknown): value is Record<string, unknown> | null {
  if (value === null) return true;
  if (typeof value !== 'object' || Array.isArray(value)) return false;
  const prototype = Object.getPrototypeOf(value);
  return prototype === Object.prototype || prototype === null;
}

function parseAuditEvent(value: unknown): UserManagementAuditEventRead {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) throw new InvalidAuditEventsResponseError();
  const event = value as Record<string, unknown>;
  const keys = Object.keys(event).sort();
  if (
    keys.length !== contractKeys.length || keys.some((key, index) => key !== contractKeys[index]) ||
    !Number.isInteger(event.id) || !isNullableInteger(event.actor_user_id) || !isNullableInteger(event.target_user_id) ||
    typeof event.event_type !== 'string' || !isNullableString(event.summary) || !isNullablePlainObject(event.details) ||
    !isValidDateTime(event.created_at)
  ) throw new InvalidAuditEventsResponseError();
  return event as unknown as UserManagementAuditEventRead;
}

export function parseAuditEvents(value: unknown): UserManagementAuditEventRead[] {
  if (!Array.isArray(value)) throw new InvalidAuditEventsResponseError();
  return value.map(parseAuditEvent);
}
