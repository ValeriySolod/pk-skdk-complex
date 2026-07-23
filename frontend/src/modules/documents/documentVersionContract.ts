export interface DocumentVersionRead {
  id: number;
  document_id: number;
  version: string;
  file_name: string;
  storage_path: string;
  checksum: string | null;
  uploaded_by: number | null;
  uploaded_at: string;
}

export class InvalidDocumentVersionsResponseError extends Error {
  constructor() {
    super('The document versions response does not match the DocumentVersionRead contract.');
    this.name = 'InvalidDocumentVersionsResponseError';
  }
}

const contractKeys = ['checksum', 'document_id', 'file_name', 'id', 'storage_path', 'uploaded_at', 'uploaded_by', 'version'];
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

function parseDocumentVersion(value: unknown): DocumentVersionRead {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) throw new InvalidDocumentVersionsResponseError();
  const version = value as Record<string, unknown>;
  const keys = Object.keys(version).sort();
  if (
    keys.length !== contractKeys.length ||
    keys.some((key, index) => key !== contractKeys[index]) ||
    !Number.isInteger(version.id) ||
    !Number.isInteger(version.document_id) ||
    typeof version.version !== 'string' ||
    typeof version.file_name !== 'string' ||
    typeof version.storage_path !== 'string' ||
    !(version.checksum === null || typeof version.checksum === 'string') ||
    !(version.uploaded_by === null || Number.isInteger(version.uploaded_by)) ||
    !isValidDateTime(version.uploaded_at)
  ) throw new InvalidDocumentVersionsResponseError();
  return version as unknown as DocumentVersionRead;
}

export function parseDocumentVersions(value: unknown): DocumentVersionRead[] {
  if (!Array.isArray(value)) throw new InvalidDocumentVersionsResponseError();
  return value.map(parseDocumentVersion);
}
