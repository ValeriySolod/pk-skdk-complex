import test from 'node:test';
import assert from 'node:assert/strict';
import { getDemoUsers, getRealUsers, getUsers } from './usersApi.ts';

const users = [{ id: 1, username: 'admin', email: null, is_active: true }];

test('real users path uses the canonical relative endpoint and validates its response', async () => {
  let path;
  assert.deepEqual(await getRealUsers(async (requestedPath) => { path = requestedPath; return users; }), users);
  assert.equal(path, '/user-management/users');
});

test('demo users path is an explicit isolated mock and returns detached values', async () => {
  const first = await getDemoUsers();
  first[0].username = 'changed';
  assert.notEqual((await getDemoUsers())[0].username, 'changed');
});

test('dispatcher isolates demo and real request paths', async () => {
  let requestCount = 0;
  let demoCount = 0;
  assert.deepEqual(await getUsers({ demoMode: true, request: async () => { requestCount += 1; return []; }, readDemoUsers: async () => { demoCount += 1; return users; } }), users);
  assert.equal(requestCount, 0);
  assert.equal(demoCount, 1);
  let requestedPath;
  assert.deepEqual(await getUsers({ demoMode: false, request: async (path) => { requestedPath = path; return users; }, readDemoUsers: async () => { demoCount += 1; return []; } }), users);
  assert.equal(requestedPath, '/user-management/users');
  assert.equal(demoCount, 1);
});
