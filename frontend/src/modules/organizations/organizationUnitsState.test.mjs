import test from 'node:test';
import assert from 'node:assert/strict';
import { ApiConfigurationError, ApiError } from '../../api/client.ts';
import { InvalidOrganizationUnitsResponseError } from './organizationUnitContract.ts';
import { loadOrganizationUnits, organizationUnitsErrorMessages } from './organizationUnitsState.ts';

const units = [{ id: 1, name: 'Operations', code: 'OPS', parent_id: null, is_active: true }];

function dependencies(result) {
  let clearCount = 0;
  return {
    value: {
      readUnits: async () => { if (result instanceof Error) throw result; return result; },
      clearSession: () => { clearCount += 1; },
    },
    clearCount: () => clearCount,
  };
}

test('organization-units orchestration represents success and empty success deterministically', async () => {
  assert.deepEqual(await loadOrganizationUnits(dependencies(units).value), { status: 'success', units });
  assert.deepEqual(await loadOrganizationUnits(dependencies([]).value), { status: 'success', units: [] });
});

test('active 401 expires the session while stale 401 has no token side effect', async () => {
  const active = dependencies(new ApiError('Unauthorized', 'http', 401));
  assert.deepEqual(await loadOrganizationUnits(active.value), { status: 'expired-session' });
  assert.equal(active.clearCount(), 1);

  const stale = dependencies(new ApiError('Unauthorized', 'http', 401));
  assert.deepEqual(await loadOrganizationUnits(stale.value, () => false), { status: 'expired-session' });
  assert.equal(stale.clearCount(), 0);
});

test('403, malformed, network, configuration, server, and other errors remain distinct and preserve token', async () => {
  const cases = [
    [new ApiError('Forbidden', 'http', 403), 'forbidden'],
    [new InvalidOrganizationUnitsResponseError(), 'malformed-response'],
    [new ApiError('Network', 'network'), 'network'],
    [new ApiConfigurationError(), 'configuration'],
    [new ApiError('Server', 'http', 503), 'server'],
    [new ApiError('Conflict', 'http', 409), 'unexpected'],
    [new Error('Unknown'), 'unexpected'],
  ];
  for (const [error, failure] of cases) {
    const setup = dependencies(error);
    assert.deepEqual(await loadOrganizationUnits(setup.value), { status: 'error', failure });
    assert.equal(setup.clearCount(), 0);
    assert.notEqual(organizationUnitsErrorMessages[failure], '');
  }
});
