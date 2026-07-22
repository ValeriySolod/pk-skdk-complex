import test from 'node:test';
import assert from 'node:assert/strict';
import { ApiConfigurationError, ApiError } from '../../api/client.ts';
import { InvalidUsersResponseError } from './userContract.ts';
import { loadUsers, usersErrorMessages } from './usersState.ts';

const users = [{ id: 1, username: 'admin', email: null, is_active: true }];
function dependencies(result) {
  let clearCount = 0;
  return { value: { readUsers: async () => { if (result instanceof Error) throw result; return result; }, clearSession: () => { clearCount += 1; } }, clearCount: () => clearCount };
}

test('users orchestration represents populated and empty success deterministically', async () => {
  assert.deepEqual(await loadUsers(dependencies(users).value), { status: 'success', users });
  assert.deepEqual(await loadUsers(dependencies([]).value), { status: 'success', users: [] });
});

test('active 401 expires the session while stale 401 has no token side effect', async () => {
  const active = dependencies(new ApiError('Unauthorized', 'http', 401));
  assert.deepEqual(await loadUsers(active.value), { status: 'expired-session' });
  assert.equal(active.clearCount(), 1);
  const stale = dependencies(new ApiError('Unauthorized', 'http', 401));
  assert.deepEqual(await loadUsers(stale.value, () => false), { status: 'expired-session' });
  assert.equal(stale.clearCount(), 0);
});

test('403 and all other failures remain distinct and preserve the token', async () => {
  const cases = [[new ApiError('Forbidden', 'http', 403), 'forbidden'], [new InvalidUsersResponseError(), 'malformed-response'], [new ApiError('Network', 'network'), 'network'], [new ApiConfigurationError(), 'configuration'], [new ApiError('Server', 'http', 503), 'server'], [new ApiError('Conflict', 'http', 409), 'unexpected'], [new Error('Unknown'), 'unexpected']];
  for (const [error, failure] of cases) {
    const setup = dependencies(error);
    assert.deepEqual(await loadUsers(setup.value), { status: 'error', failure });
    assert.equal(setup.clearCount(), 0);
    assert.notEqual(usersErrorMessages[failure], '');
  }
});
