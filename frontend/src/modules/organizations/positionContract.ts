export interface PositionRead {
  id: number;
  title: string;
  code: string | null;
  organization_unit_id: number;
  is_active: boolean;
}

export class InvalidPositionsResponseError extends Error {
  constructor() {
    super('The positions response does not match the PositionRead contract.');
    this.name = 'InvalidPositionsResponseError';
  }
}

const contractKeys = ['code', 'id', 'is_active', 'organization_unit_id', 'title'];

function parsePosition(value: unknown): PositionRead {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) {
    throw new InvalidPositionsResponseError();
  }

  const position = value as Record<string, unknown>;
  const keys = Object.keys(position).sort();
  if (
    keys.length !== contractKeys.length ||
    keys.some((key, index) => key !== contractKeys[index]) ||
    !Number.isInteger(position.id) ||
    typeof position.title !== 'string' ||
    (typeof position.code !== 'string' && position.code !== null) ||
    !Number.isInteger(position.organization_unit_id) ||
    typeof position.is_active !== 'boolean'
  ) {
    throw new InvalidPositionsResponseError();
  }

  return {
    id: position.id as number,
    title: position.title,
    code: position.code,
    organization_unit_id: position.organization_unit_id as number,
    is_active: position.is_active,
  };
}

export function parsePositions(value: unknown): PositionRead[] {
  if (!Array.isArray(value)) throw new InvalidPositionsResponseError();
  return value.map(parsePosition);
}
