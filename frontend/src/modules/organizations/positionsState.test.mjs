import test from 'node:test';
import assert from 'node:assert/strict';
import { ApiConfigurationError, ApiError } from '../../api/client.ts';
import { InvalidPositionsResponseError } from './positionContract.ts';
import { loadPositions, positionsErrorMessages } from './positionsState.ts';

const positions = [{ id: 1, title: 'Inspector', code: 'INSP', organization_unit_id: 2, is_active: true }];

function dependencies(result) {
  let clearCount = 0;
  return {
    value: {
      readPositions: async () => { if (result instanceof Error) throw result; return result; },
      clearSession: () => { clearCount += 1; },
    },
    clearCount: () => clearCount,
  };
}

test('positions orchestration represents populated and empty success deterministically', async () => {
  assert.deepEqual(await loadPositions(dependencies(positions).value), { status: 'success', positions });
  assert.deepEqual(await loadPositions(dependencies([]).value), { status: 'success', positions: [] });
});

test('active 401 expires the session while stale 401 has no token side effect', async () => {
  const active = dependencies(new ApiError('Unauthorized', 'http', 401));
  assert.deepEqual(await loadPositions(active.value), { status: 'expired-session' });
  assert.equal(active.clearCount(), 1);
  const stale = dependencies(new ApiError('Unauthorized', 'http', 401));
  assert.deepEqual(await loadPositions(stale.value, () => false), { status: 'expired-session' });
  assert.equal(stale.clearCount(), 0);
});

test('403, malformed, network, configuration, server, and unexpected errors remain distinct and preserve token', async () => {
  const cases = [
    [new ApiError('Forbidden', 'http', 403), 'forbidden'],
    [new InvalidPositionsResponseError(), 'malformed-response'],
    [new ApiError('Network', 'network'), 'network'],
    [new ApiConfigurationError(), 'configuration'],
    [new ApiError('Server', 'http', 503), 'server'],
    [new ApiError('Conflict', 'http', 409), 'unexpected'],
    [new Error('Unknown'), 'unexpected'],
  ];
  for (const [error, failure] of cases) {
    const setup = dependencies(error);
    assert.deepEqual(await loadPositions(setup.value), { status: 'error', failure });
    assert.equal(setup.clearCount(), 0);
    assert.notEqual(positionsErrorMessages[failure], '');
  }
});
