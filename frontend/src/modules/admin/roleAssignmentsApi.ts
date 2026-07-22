import { apiRequest } from '../../api/client.ts';
import { IS_DEMO_MODE } from '../../shared/config.ts';
import { parseRoleAssignments, type UserManagementRoleAssignmentRead } from './roleAssignmentContract.ts';

const ROLE_ASSIGNMENTS_PATH = '/user-management/role-assignments';
const demoRoleAssignments: UserManagementRoleAssignmentRead[] = [{ id: 1, user_id: 1, role_code: 'system.admin', scope_type: null, scope_id: null, is_active: true, assigned_by_user_id: null, assigned_at: '2026-01-01T00:00:00Z', revoked_at: null }];

export type RoleAssignmentsRequest = (path: string) => Promise<unknown>;
export type RoleAssignmentsApiDependencies = { demoMode: boolean; request: RoleAssignmentsRequest; readDemoRoleAssignments: () => Promise<UserManagementRoleAssignmentRead[]> };
export async function getRealRoleAssignments(request: RoleAssignmentsRequest = apiRequest): Promise<UserManagementRoleAssignmentRead[]> { return parseRoleAssignments(await request(ROLE_ASSIGNMENTS_PATH)); }
export async function getDemoRoleAssignments(): Promise<UserManagementRoleAssignmentRead[]> { return demoRoleAssignments.map((assignment) => ({ ...assignment })); }
const defaultDependencies: RoleAssignmentsApiDependencies = { demoMode: IS_DEMO_MODE, request: apiRequest, readDemoRoleAssignments: getDemoRoleAssignments };
export function getRoleAssignments(dependencies: RoleAssignmentsApiDependencies = defaultDependencies): Promise<UserManagementRoleAssignmentRead[]> { return dependencies.demoMode ? dependencies.readDemoRoleAssignments() : getRealRoleAssignments(dependencies.request); }
