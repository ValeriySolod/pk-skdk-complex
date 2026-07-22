import { apiRequest } from '../../api/client.ts';
import { IS_DEMO_MODE } from '../../shared/config.ts';
import { parseAuditEvents, type UserManagementAuditEventRead } from './auditEventContract.ts';

const AUDIT_EVENTS_PATH = '/user-management/audit-events';
const demoAuditEvents: UserManagementAuditEventRead[] = [{ id: 1, actor_user_id: 1, target_user_id: null, event_type: 'user.viewed', summary: 'User management viewed', details: null, created_at: '2026-01-01T00:00:00Z' }];

export type AuditEventsRequest = (path: string) => Promise<unknown>;
export type AuditEventsApiDependencies = { demoMode: boolean; request: AuditEventsRequest; readDemoAuditEvents: () => Promise<UserManagementAuditEventRead[]> };
export async function getRealAuditEvents(request: AuditEventsRequest = apiRequest): Promise<UserManagementAuditEventRead[]> { return parseAuditEvents(await request(AUDIT_EVENTS_PATH)); }
export async function getDemoAuditEvents(): Promise<UserManagementAuditEventRead[]> { return demoAuditEvents.map((event) => ({ ...event, details: event.details === null ? null : { ...event.details } })); }
const defaultDependencies: AuditEventsApiDependencies = { demoMode: IS_DEMO_MODE, request: apiRequest, readDemoAuditEvents: getDemoAuditEvents };
export function getAuditEvents(dependencies: AuditEventsApiDependencies = defaultDependencies): Promise<UserManagementAuditEventRead[]> { return dependencies.demoMode ? dependencies.readDemoAuditEvents() : getRealAuditEvents(dependencies.request); }
