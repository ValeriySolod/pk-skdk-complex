import { apiRequest } from '../../api/client.ts';
import { IS_DEMO_MODE } from '../../shared/config.ts';
import { parseUsers, type UserManagementUserRead } from './userContract.ts';

const USERS_PATH = '/user-management/users';
const demoUsers: UserManagementUserRead[] = [
  { id: 1, username: 'demo.admin', email: 'admin@example.test', is_active: true },
  { id: 2, username: 'demo.viewer', email: null, is_active: false },
];

export type UsersRequest = (path: string) => Promise<unknown>;
export type UsersApiDependencies = {
  demoMode: boolean;
  request: UsersRequest;
  readDemoUsers: () => Promise<UserManagementUserRead[]>;
};

export async function getRealUsers(request: UsersRequest = apiRequest): Promise<UserManagementUserRead[]> {
  return parseUsers(await request(USERS_PATH));
}

export async function getDemoUsers(): Promise<UserManagementUserRead[]> {
  return demoUsers.map((user) => ({ ...user }));
}

const defaultDependencies: UsersApiDependencies = {
  demoMode: IS_DEMO_MODE,
  request: apiRequest,
  readDemoUsers: getDemoUsers,
};

export function getUsers(dependencies: UsersApiDependencies = defaultDependencies): Promise<UserManagementUserRead[]> {
  return dependencies.demoMode ? dependencies.readDemoUsers() : getRealUsers(dependencies.request);
}
