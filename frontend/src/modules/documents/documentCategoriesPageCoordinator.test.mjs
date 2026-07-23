import test from 'node:test';
import assert from 'node:assert/strict';
import { createDocumentCategoriesPageCoordinator } from './documentCategoriesPageCoordinator.ts';

function deferred() { let resolve; const promise = new Promise((res) => { resolve = res; }); return { promise, resolve }; }
function harness(loadState) {
  const states = []; let navigations = 0;
  const coordinator = createDocumentCategoriesPageCoordinator({ applyState: (state) => states.push(state), navigateToLogin: () => { navigations += 1; }, loadState });
  return { coordinator, states, navigations: () => navigations };
}

test('document categories coordinator integrates loading, error, retry, empty, and success states', async () => {
  let count = 0;
  const current = harness(async () => (++count === 1 ? { status: 'error', failure: 'network' } : { status: 'success', categories: [] }));
  await current.coordinator.load(); await current.coordinator.load();
  assert.deepEqual(current.states, [{ status: 'loading' }, { status: 'error', failure: 'network' }, { status: 'loading' }, { status: 'success', categories: [] }]);
});

test('document categories coordinator suppresses stale 401 and unmounted results', async () => {
  const stale = deferred(); const latest = deferred(); const queue = [stale, latest];
  const current = harness(async () => queue.shift().promise);
  const first = current.coordinator.load(); const second = current.coordinator.load();
  stale.resolve({ status: 'expired-session' }); await first;
  latest.resolve({ status: 'success', categories: [{ id: 1 }] }); await second;
  assert.equal(current.navigations(), 0);
  assert.deepEqual(current.states.at(-1), { status: 'success', categories: [{ id: 1 }] });
  const pending = deferred(); const unmounted = harness(async () => pending.promise);
  const load = unmounted.coordinator.load(); unmounted.coordinator.invalidate();
  pending.resolve({ status: 'success', categories: [] }); await load;
  assert.deepEqual(unmounted.states, [{ status: 'loading' }]);
});
