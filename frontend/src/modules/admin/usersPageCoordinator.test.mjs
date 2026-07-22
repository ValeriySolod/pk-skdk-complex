import test from 'node:test';
import assert from 'node:assert/strict';
import { ApiError } from '../../api/client.ts';
import { createUsersPageCoordinator } from './usersPageCoordinator.ts';
import { loadUsers } from './usersState.ts';

const users = [{ id: 1, username: 'admin', email: null, is_active: true }];
function deferred() { let resolve; let reject; const promise = new Promise((res, rej) => { resolve = res; reject = rej; }); return { promise, resolve, reject }; }
function harness(loadState) { const states = []; let navigationCount = 0; const coordinator = createUsersPageCoordinator({ applyState: (state) => states.push(state), navigateToLogin: () => { navigationCount += 1; }, loadState }); return { coordinator, states, navigationCount: () => navigationCount }; }

test('coordinator applies loading then success and retry transitions', async () => {
  let count = 0;
  const setup = harness(async () => (++count === 1 ? { status: 'error', failure: 'network' } : { status: 'success', users }));
  await setup.coordinator.load(); await setup.coordinator.load();
  assert.deepEqual(setup.states, [{ status: 'loading' }, { status: 'error', failure: 'network' }, { status: 'loading' }, { status: 'success', users }]);
});

test('new generations and unmount invalidation suppress stale results and navigation', async () => {
  const stale = deferred(); const current = deferred(); const requests = [stale, current];
  const setup = harness(async () => requests.shift().promise);
  const staleLoad = setup.coordinator.load(); const currentLoad = setup.coordinator.load();
  stale.resolve({ status: 'error', failure: 'server' }); await staleLoad;
  current.resolve({ status: 'success', users: [] }); await currentLoad;
  assert.deepEqual(setup.states, [{ status: 'loading' }, { status: 'loading' }, { status: 'success', users: [] }]);
  const pending = deferred(); const unmounted = harness(async () => pending.promise); const load = unmounted.coordinator.load(); unmounted.coordinator.invalidate(); pending.resolve({ status: 'expired-session' }); await load;
  assert.deepEqual(unmounted.states, [{ status: 'loading' }]); assert.equal(unmounted.navigationCount(), 0);
});

test('only active 401 clears the token and navigates', async () => {
  let clearCount = 0;
  const active = harness((isActive) => loadUsers({ readUsers: async () => { throw new ApiError('Unauthorized', 'http', 401); }, clearSession: () => { clearCount += 1; } }, isActive));
  await active.coordinator.load(); assert.equal(clearCount, 1); assert.equal(active.navigationCount(), 1);
  const stale = deferred(); const current = deferred(); const requests = [stale, current]; clearCount = 0;
  const setup = harness((isActive) => loadUsers({ readUsers: () => requests.shift().promise, clearSession: () => { clearCount += 1; } }, isActive));
  const staleLoad = setup.coordinator.load(); const currentLoad = setup.coordinator.load(); stale.reject(new ApiError('Unauthorized', 'http', 401)); await staleLoad; current.resolve([]); await currentLoad;
  assert.equal(clearCount, 0); assert.equal(setup.navigationCount(), 0); assert.deepEqual(setup.states.at(-1), { status: 'success', users: [] });
});
