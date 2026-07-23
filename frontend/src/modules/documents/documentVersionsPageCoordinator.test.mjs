import test from 'node:test';
import assert from 'node:assert/strict';
import { createDocumentVersionsPageCoordinator } from './documentVersionsPageCoordinator.ts';

function deferred() { let resolve; const promise = new Promise((res) => { resolve = res; }); return { promise, resolve }; }
function harness(loadState) {
  const states = []; let navigations = 0;
  const coordinator = createDocumentVersionsPageCoordinator({ applyState: (state) => states.push(state), navigateToLogin: () => { navigations += 1; }, loadState });
  return { coordinator, states, navigations: () => navigations };
}

test('document versions coordinator integrates selection, loading, error, retry, empty, and clear states', async () => {
  let count = 0;
  const current = harness(async (documentId) => (++count === 1 ? { status: 'error', documentId, failure: 'network' } : { status: 'success', documentId, versions: [] }));
  await current.coordinator.load(7); await current.coordinator.load(7); current.coordinator.clear();
  assert.deepEqual(current.states, [{ status: 'loading', documentId: 7 }, { status: 'error', documentId: 7, failure: 'network' }, { status: 'loading', documentId: 7 }, { status: 'success', documentId: 7, versions: [] }, { status: 'unselected' }]);
});

test('previous selection, stale 401, and unmounted results cannot replace current state', async () => {
  const previous = deferred(); const selected = deferred(); const queue = [previous, selected];
  const current = harness(async () => queue.shift().promise);
  const first = current.coordinator.load(1); const second = current.coordinator.load(2);
  previous.resolve({ status: 'expired-session', documentId: 1 }); await first;
  selected.resolve({ status: 'success', documentId: 2, versions: [{ id: 2 }] }); await second;
  assert.equal(current.navigations(), 0);
  assert.deepEqual(current.states.at(-1), { status: 'success', documentId: 2, versions: [{ id: 2 }] });
  const pending = deferred(); const unmounted = harness(async () => pending.promise);
  const load = unmounted.coordinator.load(3); unmounted.coordinator.invalidate();
  pending.resolve({ status: 'success', documentId: 3, versions: [] }); await load;
  assert.deepEqual(unmounted.states, [{ status: 'loading', documentId: 3 }]);
});
