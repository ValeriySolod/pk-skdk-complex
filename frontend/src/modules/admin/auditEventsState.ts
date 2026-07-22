import { ApiConfigurationError, ApiError, removeToken } from '../../api/client.ts';
import { InvalidAuditEventsResponseError, type UserManagementAuditEventRead } from './auditEventContract.ts';
import { getAuditEvents } from './auditEventsApi.ts';

export type AuditEventsFailure = 'forbidden' | 'malformed-response' | 'network' | 'configuration' | 'server' | 'unexpected';
export type AuditEventsState = { status: 'loading' } | { status: 'success'; auditEvents: UserManagementAuditEventRead[] } | { status: 'expired-session' } | { status: 'error'; failure: AuditEventsFailure };
export type AuditEventsDependencies = { readAuditEvents: () => Promise<UserManagementAuditEventRead[]>; clearSession: () => void };
const defaultDependencies: AuditEventsDependencies = { readAuditEvents: getAuditEvents, clearSession: removeToken };

export async function loadAuditEvents(dependencies: AuditEventsDependencies = defaultDependencies, isRequestActive: () => boolean = () => true): Promise<AuditEventsState> {
  try { return { status: 'success', auditEvents: await dependencies.readAuditEvents() }; }
  catch (error: unknown) {
    if (error instanceof ApiError && error.kind === 'http' && error.status === 401) { if (isRequestActive()) dependencies.clearSession(); return { status: 'expired-session' }; }
    if (error instanceof ApiError && error.kind === 'http' && error.status === 403) return { status: 'error', failure: 'forbidden' };
    if (error instanceof InvalidAuditEventsResponseError) return { status: 'error', failure: 'malformed-response' };
    if (error instanceof ApiConfigurationError) return { status: 'error', failure: 'configuration' };
    if (error instanceof ApiError && error.kind === 'network') return { status: 'error', failure: 'network' };
    if (error instanceof ApiError && error.kind === 'http' && (error.status ?? 0) >= 500) return { status: 'error', failure: 'server' };
    return { status: 'error', failure: 'unexpected' };
  }
}

export const auditEventsErrorMessages: Record<AuditEventsFailure, string> = {
  forbidden: 'You do not have permission to view audit events.',
  'malformed-response': 'The server returned an invalid audit events response.',
  network: 'The server could not be reached. Check the network connection and retry.',
  configuration: 'The backend API address is not configured correctly.',
  server: 'The server could not load audit events. Retry later.',
  unexpected: 'Audit events could not be loaded. Retry the request.',
};
