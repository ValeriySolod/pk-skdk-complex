import { ApiConfigurationError, ApiError, removeToken } from '../../api/client.ts';
import { InvalidProfilesResponseError, type UserManagementProfileRead } from './profileContract.ts';
import { getProfiles } from './profilesApi.ts';

export type ProfilesFailure = 'forbidden' | 'malformed-response' | 'network' | 'configuration' | 'server' | 'unexpected';
export type ProfilesState = { status: 'loading' } | { status: 'success'; profiles: UserManagementProfileRead[] } | { status: 'expired-session' } | { status: 'error'; failure: ProfilesFailure };
export type ProfilesDependencies = { readProfiles: () => Promise<UserManagementProfileRead[]>; clearSession: () => void };
const defaultDependencies: ProfilesDependencies = { readProfiles: getProfiles, clearSession: removeToken };

export async function loadProfiles(dependencies: ProfilesDependencies = defaultDependencies, isRequestActive: () => boolean = () => true): Promise<ProfilesState> {
  try { return { status: 'success', profiles: await dependencies.readProfiles() }; }
  catch (error: unknown) {
    if (error instanceof ApiError && error.kind === 'http' && error.status === 401) { if (isRequestActive()) dependencies.clearSession(); return { status: 'expired-session' }; }
    if (error instanceof ApiError && error.kind === 'http' && error.status === 403) return { status: 'error', failure: 'forbidden' };
    if (error instanceof InvalidProfilesResponseError) return { status: 'error', failure: 'malformed-response' };
    if (error instanceof ApiConfigurationError) return { status: 'error', failure: 'configuration' };
    if (error instanceof ApiError && error.kind === 'network') return { status: 'error', failure: 'network' };
    if (error instanceof ApiError && error.kind === 'http' && (error.status ?? 0) >= 500) return { status: 'error', failure: 'server' };
    return { status: 'error', failure: 'unexpected' };
  }
}

export const profilesErrorMessages: Record<ProfilesFailure, string> = {
  forbidden: 'You do not have permission to view profiles.',
  'malformed-response': 'The server returned an invalid profiles response.',
  network: 'The server could not be reached. Check the network connection and retry.',
  configuration: 'The backend API address is not configured correctly.',
  server: 'The server could not load profiles. Retry later.',
  unexpected: 'Profiles could not be loaded. Retry the request.',
};
