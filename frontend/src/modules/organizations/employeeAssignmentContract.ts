export interface EmployeeAssignmentRead {
  id: number;
  user_id: number;
  position_id: number;
  start_date: string | null;
  end_date: string | null;
  is_active: boolean;
}

export class InvalidEmployeeAssignmentsResponseError extends Error {
  constructor() {
    super('The employee assignments response does not match the EmployeeAssignmentRead contract.');
    this.name = 'InvalidEmployeeAssignmentsResponseError';
  }
}

const contractKeys = ['end_date', 'id', 'is_active', 'position_id', 'start_date', 'user_id'];
const isoDatePattern = /^(\d{4})-(\d{2})-(\d{2})$/;

function isIsoDate(value: unknown): value is string {
  if (typeof value !== 'string') return false;
  const match = isoDatePattern.exec(value);
  if (match === null) return false;
  const year = Number(match[1]);
  const month = Number(match[2]);
  const day = Number(match[3]);
  if (year < 1 || month < 1 || month > 12) return false;
  const isLeapYear = year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0);
  const daysInMonth = [31, isLeapYear ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  return day >= 1 && day <= daysInMonth[month - 1];
}

function parseNullableDate(value: unknown): string | null {
  if (value === null) return null;
  if (!isIsoDate(value)) throw new InvalidEmployeeAssignmentsResponseError();
  return value;
}

function parseEmployeeAssignment(value: unknown): EmployeeAssignmentRead {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) {
    throw new InvalidEmployeeAssignmentsResponseError();
  }

  const assignment = value as Record<string, unknown>;
  const keys = Object.keys(assignment).sort();
  if (
    keys.length !== contractKeys.length ||
    keys.some((key, index) => key !== contractKeys[index]) ||
    !Number.isInteger(assignment.id) ||
    !Number.isInteger(assignment.user_id) ||
    !Number.isInteger(assignment.position_id) ||
    typeof assignment.is_active !== 'boolean'
  ) {
    throw new InvalidEmployeeAssignmentsResponseError();
  }

  return {
    id: assignment.id as number,
    user_id: assignment.user_id as number,
    position_id: assignment.position_id as number,
    start_date: parseNullableDate(assignment.start_date),
    end_date: parseNullableDate(assignment.end_date),
    is_active: assignment.is_active,
  };
}

export function parseEmployeeAssignments(value: unknown): EmployeeAssignmentRead[] {
  if (!Array.isArray(value)) throw new InvalidEmployeeAssignmentsResponseError();
  return value.map(parseEmployeeAssignment);
}
