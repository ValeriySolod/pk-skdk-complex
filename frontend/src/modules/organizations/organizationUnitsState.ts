import { ApiConfigurationError, ApiError, removeToken } from '../../api/client.ts';
import { InvalidOrganizationUnitsResponseError, type OrganizationUnitRead } from './organizationUnitContract.ts';
import { getOrganizationUnits } from './organizationUnitsApi.ts';

export type OrganizationUnitsFailure =
  | 'forbidden'
  | 'malformed-response'
  | 'network'
  | 'configuration'
  | 'server'
  | 'unexpected';

export type OrganizationUnitsState =
  | { status: 'loading' }
  | { status: 'success'; units: OrganizationUnitRead[] }
  | { status: 'expired-session' }
  | { status: 'error'; failure: OrganizationUnitsFailure };

export type OrganizationUnitsDependencies = {
  readUnits: () => Promise<OrganizationUnitRead[]>;
  clearSession: () => void;
};

const defaultDependencies: OrganizationUnitsDependencies = {
  readUnits: getOrganizationUnits,
  clearSession: removeToken,
};

export async function loadOrganizationUnits(
  dependencies: OrganizationUnitsDependencies = defaultDependencies,
  isRequestActive: () => boolean = () => true,
): Promise<OrganizationUnitsState> {
  try {
    return { status: 'success', units: await dependencies.readUnits() };
  } catch (error: unknown) {
    if (error instanceof ApiError && error.kind === 'http' && error.status === 401) {
      if (isRequestActive()) dependencies.clearSession();
      return { status: 'expired-session' };
    }
    if (error instanceof ApiError && error.kind === 'http' && error.status === 403) return { status: 'error', failure: 'forbidden' };
    if (error instanceof InvalidOrganizationUnitsResponseError) return { status: 'error', failure: 'malformed-response' };
    if (error instanceof ApiConfigurationError) return { status: 'error', failure: 'configuration' };
    if (error instanceof ApiError && error.kind === 'network') return { status: 'error', failure: 'network' };
    if (error instanceof ApiError && error.kind === 'http' && (error.status ?? 0) >= 500) return { status: 'error', failure: 'server' };
    return { status: 'error', failure: 'unexpected' };
  }
}

export const organizationUnitsErrorMessages: Record<OrganizationUnitsFailure, string> = {
  forbidden: 'You do not have permission to view organization units.',
  'malformed-response': 'The server returned an invalid organization-units response.',
  network: 'The server could not be reached. Check the network connection and retry.',
  configuration: 'The backend API address is not configured correctly.',
  server: 'The server could not load organization units. Retry later.',
  unexpected: 'Organization units could not be loaded. Retry the request.',
};
