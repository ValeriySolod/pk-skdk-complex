import test from 'node:test';
import assert from 'node:assert/strict';
import { ApiError } from '../../api/client.ts';
import { createEmployeeAssignmentsPageCoordinator } from './employeeAssignmentsPageCoordinator.ts';
import { loadEmployeeAssignments } from './employeeAssignmentsState.ts';

const assignments = [{ id: 1, user_id: 4, position_id: 2, start_date: null, end_date: null, is_active: true }];

function deferred() {
  let resolve;
  let reject;
  const promise = new Promise((resolvePromise, rejectPromise) => {
    resolve = resolvePromise;
    reject = rejectPromise;
  });
  return { promise, resolve, reject };
}

function harness(loadState) {
  const states = [];
  let navigationCount = 0;
  const coordinator = createEmployeeAssignmentsPageCoordinator({
    applyState: (state) => states.push(state),
    navigateToLogin: () => { navigationCount += 1; },
    loadState,
  });
  return { coordinator, states, navigationCount: () => navigationCount };
}

test('coordinator applies loading then success and repeats both transitions on retry', async () => {
  let requestCount = 0;
  const setup = harness(async () => {
    requestCount += 1;
    return requestCount === 1 ? { status: 'error', failure: 'network' } : { status: 'success', assignments };
  });
  await setup.coordinator.load();
  await setup.coordinator.load();
  assert.deepEqual(setup.states, [
    { status: 'loading' },
    { status: 'error', failure: 'network' },
    { status: 'loading' },
    { status: 'success', assignments },
  ]);
});

test('new generations suppress stale results', async () => {
  const stale = deferred();
  const current = deferred();
  const requests = [stale, current];
  const setup = harness(async () => (await requests.shift().promise));
  const staleLoad = setup.coordinator.load();
  const currentLoad = setup.coordinator.load();
  stale.resolve({ status: 'error', failure: 'server' });
  await staleLoad;
  current.resolve({ status: 'success', assignments: [] });
  await currentLoad;
  assert.deepEqual(setup.states, [
    { status: 'loading' },
    { status: 'loading' },
    { status: 'success', assignments: [] },
  ]);
});

test('invalidation suppresses pending state application and navigation', async () => {
  const pending = deferred();
  const setup = harness(async () => pending.promise);
  const load = setup.coordinator.load();
  setup.coordinator.invalidate();
  pending.resolve({ status: 'expired-session' });
  await load;
  assert.deepEqual(setup.states, [{ status: 'loading' }]);
  assert.equal(setup.navigationCount(), 0);
});

test('active 401 clears the token and navigates to login', async () => {
  let clearCount = 0;
  const setup = harness((isRequestActive) => loadEmployeeAssignments({
    readEmployeeAssignments: async () => { throw new ApiError('Unauthorized', 'http', 401); },
    clearSession: () => { clearCount += 1; },
  }, isRequestActive));
  await setup.coordinator.load();
  assert.deepEqual(setup.states, [{ status: 'loading' }]);
  assert.equal(clearCount, 1);
  assert.equal(setup.navigationCount(), 1);
});

test('stale 401 cannot clear the token, navigate, or replace the current result', async () => {
  const stale = deferred();
  const current = deferred();
  const requests = [stale, current];
  let clearCount = 0;
  const setup = harness((isRequestActive) => loadEmployeeAssignments({
    readEmployeeAssignments: () => requests.shift().promise,
    clearSession: () => { clearCount += 1; },
  }, isRequestActive));
  const staleLoad = setup.coordinator.load();
  const currentLoad = setup.coordinator.load();
  stale.reject(new ApiError('Unauthorized', 'http', 401));
  await staleLoad;
  current.resolve([]);
  await currentLoad;
  assert.deepEqual(setup.states, [
    { status: 'loading' },
    { status: 'loading' },
    { status: 'success', assignments: [] },
  ]);
  assert.equal(clearCount, 0);
  assert.equal(setup.navigationCount(), 0);
});
