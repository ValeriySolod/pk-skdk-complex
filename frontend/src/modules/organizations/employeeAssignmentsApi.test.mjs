import test from 'node:test';
import assert from 'node:assert/strict';
import { getDemoEmployeeAssignments, getEmployeeAssignments, getRealEmployeeAssignments } from './employeeAssignmentsApi.ts';

const assignments = [{ id: 1, user_id: 4, position_id: 2, start_date: '2026-01-01', end_date: null, is_active: true }];

test('real employee assignments path uses the canonical relative API endpoint and validates its response', async () => {
  let path;
  const result = await getRealEmployeeAssignments(async (requestedPath) => {
    path = requestedPath;
    return assignments;
  });
  assert.equal(path, '/organization-structure/assignments');
  assert.deepEqual(result, assignments);
});

test('demo employee assignments path is an explicit isolated mock and returns detached values', async () => {
  const first = await getDemoEmployeeAssignments();
  first[0].user_id = 999;
  const second = await getDemoEmployeeAssignments();
  assert.notEqual(second[0].user_id, 999);
});

test('public dispatcher uses demo data without invoking the canonical API request', async () => {
  let requestCount = 0;
  let demoCount = 0;
  const result = await getEmployeeAssignments({
    demoMode: true,
    request: async () => { requestCount += 1; return []; },
    readDemoEmployeeAssignments: async () => { demoCount += 1; return assignments; },
  });
  assert.deepEqual(result, assignments);
  assert.equal(demoCount, 1);
  assert.equal(requestCount, 0);
});

test('public dispatcher uses the real canonical request path outside demo mode', async () => {
  let requestedPath;
  let demoCount = 0;
  const result = await getEmployeeAssignments({
    demoMode: false,
    request: async (path) => { requestedPath = path; return assignments; },
    readDemoEmployeeAssignments: async () => { demoCount += 1; return []; },
  });
  assert.deepEqual(result, assignments);
  assert.equal(requestedPath, '/organization-structure/assignments');
  assert.equal(demoCount, 0);
});
