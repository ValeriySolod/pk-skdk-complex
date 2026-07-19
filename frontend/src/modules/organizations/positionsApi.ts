import { apiRequest } from '../../api/client.ts';
import { IS_DEMO_MODE } from '../../shared/config.ts';
import { parsePositions, type PositionRead } from './positionContract.ts';

const POSITIONS_PATH = '/organization-structure/positions';

const demoPositions: PositionRead[] = [
  { id: 1, title: 'Demo Director', code: 'DEMO-DIR', organization_unit_id: 1, is_active: true },
  { id: 2, title: 'Demo Registrar', code: null, organization_unit_id: 2, is_active: true },
];

export type PositionsRequest = (path: string) => Promise<unknown>;
export type PositionsApiDependencies = {
  demoMode: boolean;
  request: PositionsRequest;
  readDemoPositions: () => Promise<PositionRead[]>;
};

export async function getRealPositions(
  request: PositionsRequest = apiRequest,
): Promise<PositionRead[]> {
  return parsePositions(await request(POSITIONS_PATH));
}

export async function getDemoPositions(): Promise<PositionRead[]> {
  return demoPositions.map((position) => ({ ...position }));
}

const defaultDependencies: PositionsApiDependencies = {
  demoMode: IS_DEMO_MODE,
  request: apiRequest,
  readDemoPositions: getDemoPositions,
};

export function getPositions(
  dependencies: PositionsApiDependencies = defaultDependencies,
): Promise<PositionRead[]> {
  return dependencies.demoMode
    ? dependencies.readDemoPositions()
    : getRealPositions(dependencies.request);
}
