import { apiRequest } from '../../api/client.ts';
import { IS_DEMO_MODE } from '../../shared/config.ts';
import { parseProfiles, type UserManagementProfileRead } from './profileContract.ts';

const PROFILES_PATH = '/user-management/profiles';
const demoProfiles: UserManagementProfileRead[] = [{
  id: 1, user_id: 1, display_name: 'Demo Administrator', personnel_number: 'DEMO-001',
  job_title: 'Administrator', phone_number: null, is_active: true, notes: null,
  created_at: '2026-01-01T00:00:00Z', updated_at: '2026-01-01T00:00:00Z',
}];

export type ProfilesRequest = (path: string) => Promise<unknown>;
export type ProfilesApiDependencies = { demoMode: boolean; request: ProfilesRequest; readDemoProfiles: () => Promise<UserManagementProfileRead[]> };

export async function getRealProfiles(request: ProfilesRequest = apiRequest): Promise<UserManagementProfileRead[]> {
  return parseProfiles(await request(PROFILES_PATH));
}
export async function getDemoProfiles(): Promise<UserManagementProfileRead[]> { return demoProfiles.map((profile) => ({ ...profile })); }
const defaultDependencies: ProfilesApiDependencies = { demoMode: IS_DEMO_MODE, request: apiRequest, readDemoProfiles: getDemoProfiles };
export function getProfiles(dependencies: ProfilesApiDependencies = defaultDependencies): Promise<UserManagementProfileRead[]> {
  return dependencies.demoMode ? dependencies.readDemoProfiles() : getRealProfiles(dependencies.request);
}
