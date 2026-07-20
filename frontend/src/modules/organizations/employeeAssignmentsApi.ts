import { apiRequest } from '../../api/client.ts';
import { IS_DEMO_MODE } from '../../shared/config.ts';
import { parseEmployeeAssignments, type EmployeeAssignmentRead } from './employeeAssignmentContract.ts';

const EMPLOYEE_ASSIGNMENTS_PATH = '/organization-structure/assignments';

const demoEmployeeAssignments: EmployeeAssignmentRead[] = [
  { id: 1, user_id: 101, position_id: 1, start_date: '2026-01-01', end_date: null, is_active: true },
  { id: 2, user_id: 102, position_id: 2, start_date: null, end_date: null, is_active: true },
];

export type EmployeeAssignmentsRequest = (path: string) => Promise<unknown>;
export type EmployeeAssignmentsApiDependencies = {
  demoMode: boolean;
  request: EmployeeAssignmentsRequest;
  readDemoEmployeeAssignments: () => Promise<EmployeeAssignmentRead[]>;
};

export async function getRealEmployeeAssignments(
  request: EmployeeAssignmentsRequest = apiRequest,
): Promise<EmployeeAssignmentRead[]> {
  return parseEmployeeAssignments(await request(EMPLOYEE_ASSIGNMENTS_PATH));
}

export async function getDemoEmployeeAssignments(): Promise<EmployeeAssignmentRead[]> {
  return demoEmployeeAssignments.map((assignment) => ({ ...assignment }));
}

const defaultDependencies: EmployeeAssignmentsApiDependencies = {
  demoMode: IS_DEMO_MODE,
  request: apiRequest,
  readDemoEmployeeAssignments: getDemoEmployeeAssignments,
};

export function getEmployeeAssignments(
  dependencies: EmployeeAssignmentsApiDependencies = defaultDependencies,
): Promise<EmployeeAssignmentRead[]> {
  return dependencies.demoMode
    ? dependencies.readDemoEmployeeAssignments()
    : getRealEmployeeAssignments(dependencies.request);
}
