import { apiRequest } from '../../api/client.ts';
import { IS_DEMO_MODE } from '../../shared/config.ts';
import { parseOrganizationUnits, type OrganizationUnitRead } from './organizationUnitContract.ts';

const ORGANIZATION_UNITS_PATH = '/organization-structure/units';

const demoOrganizationUnits: OrganizationUnitRead[] = [
  { id: 1, name: 'Demo Head Office', code: 'DEMO-HQ', parent_id: null, is_active: true },
  { id: 2, name: 'Demo Registry Unit', code: 'DEMO-REG', parent_id: 1, is_active: true },
];

export type OrganizationUnitsRequest = (path: string) => Promise<unknown>;
export type OrganizationUnitsApiDependencies = {
  demoMode: boolean;
  request: OrganizationUnitsRequest;
  readDemoUnits: () => Promise<OrganizationUnitRead[]>;
};

export async function getRealOrganizationUnits(
  request: OrganizationUnitsRequest = apiRequest,
): Promise<OrganizationUnitRead[]> {
  return parseOrganizationUnits(await request(ORGANIZATION_UNITS_PATH));
}

export async function getDemoOrganizationUnits(): Promise<OrganizationUnitRead[]> {
  return demoOrganizationUnits.map((unit) => ({ ...unit }));
}

const defaultDependencies: OrganizationUnitsApiDependencies = {
  demoMode: IS_DEMO_MODE,
  request: apiRequest,
  readDemoUnits: getDemoOrganizationUnits,
};

export function getOrganizationUnits(
  dependencies: OrganizationUnitsApiDependencies = defaultDependencies,
): Promise<OrganizationUnitRead[]> {
  return dependencies.demoMode
    ? dependencies.readDemoUnits()
    : getRealOrganizationUnits(dependencies.request);
}
