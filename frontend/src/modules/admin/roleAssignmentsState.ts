import { ApiConfigurationError, ApiError, removeToken } from '../../api/client.ts';
import { InvalidRoleAssignmentsResponseError, type UserManagementRoleAssignmentRead } from './roleAssignmentContract.ts';
import { getRoleAssignments } from './roleAssignmentsApi.ts';

export type RoleAssignmentsFailure = 'forbidden' | 'malformed-response' | 'network' | 'configuration' | 'server' | 'unexpected';
export type RoleAssignmentsState = { status: 'loading' } | { status: 'success'; roleAssignments: UserManagementRoleAssignmentRead[] } | { status: 'expired-session' } | { status: 'error'; failure: RoleAssignmentsFailure };
export type RoleAssignmentsDependencies = { readRoleAssignments: () => Promise<UserManagementRoleAssignmentRead[]>; clearSession: () => void };
const defaultDependencies: RoleAssignmentsDependencies = { readRoleAssignments: getRoleAssignments, clearSession: removeToken };

export async function loadRoleAssignments(dependencies: RoleAssignmentsDependencies = defaultDependencies, isRequestActive: () => boolean = () => true): Promise<RoleAssignmentsState> {
  try { return { status: 'success', roleAssignments: await dependencies.readRoleAssignments() }; }
  catch (error: unknown) {
    if (error instanceof ApiError && error.kind === 'http' && error.status === 401) { if (isRequestActive()) dependencies.clearSession(); return { status: 'expired-session' }; }
    if (error instanceof ApiError && error.kind === 'http' && error.status === 403) return { status: 'error', failure: 'forbidden' };
    if (error instanceof InvalidRoleAssignmentsResponseError) return { status: 'error', failure: 'malformed-response' };
    if (error instanceof ApiConfigurationError) return { status: 'error', failure: 'configuration' };
    if (error instanceof ApiError && error.kind === 'network') return { status: 'error', failure: 'network' };
    if (error instanceof ApiError && error.kind === 'http' && (error.status ?? 0) >= 500) return { status: 'error', failure: 'server' };
    return { status: 'error', failure: 'unexpected' };
  }
}

export const roleAssignmentsErrorMessages: Record<RoleAssignmentsFailure, string> = {
  forbidden: 'You do not have permission to view role assignments.',
  'malformed-response': 'The server returned an invalid role assignments response.',
  network: 'The server could not be reached. Check the network connection and retry.',
  configuration: 'The backend API address is not configured correctly.',
  server: 'The server could not load role assignments. Retry later.',
  unexpected: 'Role assignments could not be loaded. Retry the request.',
};
