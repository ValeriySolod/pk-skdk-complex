import test from 'node:test';
import assert from 'node:assert/strict';
import { ApiConfigurationError, ApiError } from '../../api/client.ts';
import { InvalidEmployeeAssignmentsResponseError } from './employeeAssignmentContract.ts';
import { employeeAssignmentsErrorMessages, loadEmployeeAssignments } from './employeeAssignmentsState.ts';

const assignments = [{ id: 1, user_id: 4, position_id: 2, start_date: null, end_date: null, is_active: true }];

function dependencies(result) {
  let clearCount = 0;
  return {
    value: {
      readEmployeeAssignments: async () => { if (result instanceof Error) throw result; return result; },
      clearSession: () => { clearCount += 1; },
    },
    clearCount: () => clearCount,
  };
}

test('employee assignments orchestration represents populated and empty success deterministically', async () => {
  assert.deepEqual(await loadEmployeeAssignments(dependencies(assignments).value), { status: 'success', assignments });
  assert.deepEqual(await loadEmployeeAssignments(dependencies([]).value), { status: 'success', assignments: [] });
});

test('active 401 expires the session while stale 401 has no token side effect', async () => {
  const active = dependencies(new ApiError('Unauthorized', 'http', 401));
  assert.deepEqual(await loadEmployeeAssignments(active.value), { status: 'expired-session' });
  assert.equal(active.clearCount(), 1);
  const stale = dependencies(new ApiError('Unauthorized', 'http', 401));
  assert.deepEqual(await loadEmployeeAssignments(stale.value, () => false), { status: 'expired-session' });
  assert.equal(stale.clearCount(), 0);
});

test('403, malformed, network, configuration, server, and unexpected errors remain distinct and preserve token', async () => {
  const cases = [
    [new ApiError('Forbidden', 'http', 403), 'forbidden'],
    [new InvalidEmployeeAssignmentsResponseError(), 'malformed-response'],
    [new ApiError('Network', 'network'), 'network'],
    [new ApiConfigurationError(), 'configuration'],
    [new ApiError('Server', 'http', 503), 'server'],
    [new ApiError('Conflict', 'http', 409), 'unexpected'],
    [new Error('Unknown'), 'unexpected'],
  ];
  for (const [error, failure] of cases) {
    const setup = dependencies(error);
    assert.deepEqual(await loadEmployeeAssignments(setup.value), { status: 'error', failure });
    assert.equal(setup.clearCount(), 0);
    assert.notEqual(employeeAssignmentsErrorMessages[failure], '');
  }
});
