import { ApiConfigurationError, ApiError, removeToken } from '../../api/client.ts';
import { InvalidEmployeeAssignmentsResponseError, type EmployeeAssignmentRead } from './employeeAssignmentContract.ts';
import { getEmployeeAssignments } from './employeeAssignmentsApi.ts';

export type EmployeeAssignmentsFailure =
  | 'forbidden'
  | 'malformed-response'
  | 'network'
  | 'configuration'
  | 'server'
  | 'unexpected';

export type EmployeeAssignmentsState =
  | { status: 'loading' }
  | { status: 'success'; assignments: EmployeeAssignmentRead[] }
  | { status: 'expired-session' }
  | { status: 'error'; failure: EmployeeAssignmentsFailure };

export type EmployeeAssignmentsDependencies = {
  readEmployeeAssignments: () => Promise<EmployeeAssignmentRead[]>;
  clearSession: () => void;
};

const defaultDependencies: EmployeeAssignmentsDependencies = {
  readEmployeeAssignments: getEmployeeAssignments,
  clearSession: removeToken,
};

export async function loadEmployeeAssignments(
  dependencies: EmployeeAssignmentsDependencies = defaultDependencies,
  isRequestActive: () => boolean = () => true,
): Promise<EmployeeAssignmentsState> {
  try {
    return { status: 'success', assignments: await dependencies.readEmployeeAssignments() };
  } catch (error: unknown) {
    if (error instanceof ApiError && error.kind === 'http' && error.status === 401) {
      if (isRequestActive()) dependencies.clearSession();
      return { status: 'expired-session' };
    }
    if (error instanceof ApiError && error.kind === 'http' && error.status === 403) return { status: 'error', failure: 'forbidden' };
    if (error instanceof InvalidEmployeeAssignmentsResponseError) return { status: 'error', failure: 'malformed-response' };
    if (error instanceof ApiConfigurationError) return { status: 'error', failure: 'configuration' };
    if (error instanceof ApiError && error.kind === 'network') return { status: 'error', failure: 'network' };
    if (error instanceof ApiError && error.kind === 'http' && (error.status ?? 0) >= 500) return { status: 'error', failure: 'server' };
    return { status: 'error', failure: 'unexpected' };
  }
}

export const employeeAssignmentsErrorMessages: Record<EmployeeAssignmentsFailure, string> = {
  forbidden: 'You do not have permission to view employee assignments.',
  'malformed-response': 'The server returned an invalid employee assignments response.',
  network: 'The server could not be reached. Check the network connection and retry.',
  configuration: 'The backend API address is not configured correctly.',
  server: 'The server could not load employee assignments. Retry later.',
  unexpected: 'Employee assignments could not be loaded. Retry the request.',
};
