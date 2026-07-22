import { ApiConfigurationError, ApiError, removeToken } from '../../api/client.ts';
import { InvalidUsersResponseError, type UserManagementUserRead } from './userContract.ts';
import { getUsers } from './usersApi.ts';

export type UsersFailure = 'forbidden' | 'malformed-response' | 'network' | 'configuration' | 'server' | 'unexpected';
export type UsersState =
  | { status: 'loading' }
  | { status: 'success'; users: UserManagementUserRead[] }
  | { status: 'expired-session' }
  | { status: 'error'; failure: UsersFailure };

export type UsersDependencies = { readUsers: () => Promise<UserManagementUserRead[]>; clearSession: () => void };
const defaultDependencies: UsersDependencies = { readUsers: getUsers, clearSession: removeToken };

export async function loadUsers(
  dependencies: UsersDependencies = defaultDependencies,
  isRequestActive: () => boolean = () => true,
): Promise<UsersState> {
  try {
    return { status: 'success', users: await dependencies.readUsers() };
  } catch (error: unknown) {
    if (error instanceof ApiError && error.kind === 'http' && error.status === 401) {
      if (isRequestActive()) dependencies.clearSession();
      return { status: 'expired-session' };
    }
    if (error instanceof ApiError && error.kind === 'http' && error.status === 403) return { status: 'error', failure: 'forbidden' };
    if (error instanceof InvalidUsersResponseError) return { status: 'error', failure: 'malformed-response' };
    if (error instanceof ApiConfigurationError) return { status: 'error', failure: 'configuration' };
    if (error instanceof ApiError && error.kind === 'network') return { status: 'error', failure: 'network' };
    if (error instanceof ApiError && error.kind === 'http' && (error.status ?? 0) >= 500) return { status: 'error', failure: 'server' };
    return { status: 'error', failure: 'unexpected' };
  }
}

export const usersErrorMessages: Record<UsersFailure, string> = {
  forbidden: 'You do not have permission to view users.',
  'malformed-response': 'The server returned an invalid users response.',
  network: 'The server could not be reached. Check the network connection and retry.',
  configuration: 'The backend API address is not configured correctly.',
  server: 'The server could not load users. Retry later.',
  unexpected: 'Users could not be loaded. Retry the request.',
};
