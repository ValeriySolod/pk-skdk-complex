export interface DocumentRead {
  id: number; title: string; document_number: string | null; description: string | null;
  document_type: string; status: string; organization_id: number | null; owner_user_id: number | null;
  created_at: string; updated_at: string;
}
export class InvalidDocumentsResponseError extends Error {
  constructor() { super('The documents response does not match the DocumentRead contract.'); this.name = 'InvalidDocumentsResponseError'; }
}
const contractKeys = ['created_at', 'description', 'document_number', 'document_type', 'id', 'organization_id', 'owner_user_id', 'status', 'title', 'updated_at'];
const dateTimePattern = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d+)?(?:Z|([+-])(\d{2}):(\d{2}))?$/;
function isValidDateTime(value: unknown): value is string {
  if (typeof value !== 'string') return false;
  const match = dateTimePattern.exec(value); if (match === null) return false;
  const [, year, month, day, hour, minute, second, , offsetHour, offsetMinute] = match;
  const [y, m, d, h, min, s] = [year, month, day, hour, minute, second].map(Number);
  if (h > 23 || min > 59 || s > 59 || Number(offsetHour ?? 0) > 23 || Number(offsetMinute ?? 0) > 59) return false;
  const date = new Date(Date.UTC(y, m - 1, d, h, min, s));
  return date.getUTCFullYear() === y && date.getUTCMonth() === m - 1 && date.getUTCDate() === d;
}
function nullableInteger(value: unknown): boolean { return value === null || Number.isInteger(value); }
function nullableString(value: unknown): boolean { return value === null || typeof value === 'string'; }
function parseDocument(value: unknown): DocumentRead {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) throw new InvalidDocumentsResponseError();
  const document = value as Record<string, unknown>; const keys = Object.keys(document).sort();
  if (keys.length !== contractKeys.length || keys.some((key, index) => key !== contractKeys[index]) ||
    !Number.isInteger(document.id) || typeof document.title !== 'string' || !nullableString(document.document_number) ||
    !nullableString(document.description) || typeof document.document_type !== 'string' || typeof document.status !== 'string' ||
    !nullableInteger(document.organization_id) || !nullableInteger(document.owner_user_id) ||
    !isValidDateTime(document.created_at) || !isValidDateTime(document.updated_at)) throw new InvalidDocumentsResponseError();
  return document as unknown as DocumentRead;
}
export function parseDocuments(value: unknown): DocumentRead[] {
  if (!Array.isArray(value)) throw new InvalidDocumentsResponseError();
  return value.map(parseDocument);
}
