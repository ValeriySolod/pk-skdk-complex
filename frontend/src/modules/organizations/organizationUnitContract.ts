export interface OrganizationUnitRead {
  id: number;
  name: string;
  code: string | null;
  parent_id: number | null;
  is_active: boolean;
}

export class InvalidOrganizationUnitsResponseError extends Error {
  constructor() {
    super('The organization-units response does not match the OrganizationUnitRead contract.');
    this.name = 'InvalidOrganizationUnitsResponseError';
  }
}

const contractKeys = ['code', 'id', 'is_active', 'name', 'parent_id'];

function parseOrganizationUnit(value: unknown): OrganizationUnitRead {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) {
    throw new InvalidOrganizationUnitsResponseError();
  }

  const unit = value as Record<string, unknown>;
  const keys = Object.keys(unit).sort();
  if (
    keys.length !== contractKeys.length ||
    keys.some((key, index) => key !== contractKeys[index]) ||
    !Number.isInteger(unit.id) ||
    typeof unit.name !== 'string' ||
    (typeof unit.code !== 'string' && unit.code !== null) ||
    (!Number.isInteger(unit.parent_id) && unit.parent_id !== null) ||
    typeof unit.is_active !== 'boolean'
  ) {
    throw new InvalidOrganizationUnitsResponseError();
  }

  return {
    id: unit.id as number,
    name: unit.name,
    code: unit.code,
    parent_id: unit.parent_id as number | null,
    is_active: unit.is_active,
  };
}

export function parseOrganizationUnits(value: unknown): OrganizationUnitRead[] {
  if (!Array.isArray(value)) throw new InvalidOrganizationUnitsResponseError();
  return value.map(parseOrganizationUnit);
}
