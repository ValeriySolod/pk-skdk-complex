import { ApiConfigurationError, ApiError, removeToken } from '../../api/client.ts';
import { InvalidPositionsResponseError, type PositionRead } from './positionContract.ts';
import { getPositions } from './positionsApi.ts';

export type PositionsFailure =
  | 'forbidden'
  | 'malformed-response'
  | 'network'
  | 'configuration'
  | 'server'
  | 'unexpected';

export type PositionsState =
  | { status: 'loading' }
  | { status: 'success'; positions: PositionRead[] }
  | { status: 'expired-session' }
  | { status: 'error'; failure: PositionsFailure };

export type PositionsDependencies = {
  readPositions: () => Promise<PositionRead[]>;
  clearSession: () => void;
};

const defaultDependencies: PositionsDependencies = {
  readPositions: getPositions,
  clearSession: removeToken,
};

export async function loadPositions(
  dependencies: PositionsDependencies = defaultDependencies,
  isRequestActive: () => boolean = () => true,
): Promise<PositionsState> {
  try {
    return { status: 'success', positions: await dependencies.readPositions() };
  } catch (error: unknown) {
    if (error instanceof ApiError && error.kind === 'http' && error.status === 401) {
      if (isRequestActive()) dependencies.clearSession();
      return { status: 'expired-session' };
    }
    if (error instanceof ApiError && error.kind === 'http' && error.status === 403) return { status: 'error', failure: 'forbidden' };
    if (error instanceof InvalidPositionsResponseError) return { status: 'error', failure: 'malformed-response' };
    if (error instanceof ApiConfigurationError) return { status: 'error', failure: 'configuration' };
    if (error instanceof ApiError && error.kind === 'network') return { status: 'error', failure: 'network' };
    if (error instanceof ApiError && error.kind === 'http' && (error.status ?? 0) >= 500) return { status: 'error', failure: 'server' };
    return { status: 'error', failure: 'unexpected' };
  }
}

export const positionsErrorMessages: Record<PositionsFailure, string> = {
  forbidden: 'You do not have permission to view positions.',
  'malformed-response': 'The server returned an invalid positions response.',
  network: 'The server could not be reached. Check the network connection and retry.',
  configuration: 'The backend API address is not configured correctly.',
  server: 'The server could not load positions. Retry later.',
  unexpected: 'Positions could not be loaded. Retry the request.',
};
