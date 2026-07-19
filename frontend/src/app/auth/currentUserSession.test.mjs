import test from 'node:test';
import assert from 'node:assert/strict';
import { ApiConfigurationError, ApiError } from '../../api/client.ts';
import { InvalidUserResponseError } from '../../api/userContract.ts';
import {
  createCurrentUserSessionRequestCoordinator,
  getCurrentUserDestination,
  getCurrentUserErrorView,
  loadCurrentUserSession,
} from './currentUserSession.ts';

const user = {
  id: 17,
  username: 'operator',
  full_name: 'Олена Коваль',
  role: 'OPERATOR',
  department: 'Канцелярія',
  is_active: true,
};

function dependencies(result, { token = 'token' } = {}) {
  let clearCount = 0;
  return {
    value: {
      readToken: () => token,
      readCurrentUser: async () => {
        if (result instanceof Error) throw result;
        return result;
      },
      clearSession: () => { clearCount += 1; },
    },
    clearCount: () => clearCount,
  };
}

test('session orchestration maps missing token directly to login without requesting a user', async () => {
  let requested = false;
  const state = await loadCurrentUserSession({
    readToken: () => null,
    readCurrentUser: async () => { requested = true; return user; },
    clearSession: () => assert.fail('missing token must not clear storage'),
  });
  assert.deepEqual(state, { status: 'anonymous', reason: 'missing-token' });
  assert.equal(getCurrentUserDestination(state), 'login');
  assert.equal(requested, false);
});

test('session orchestration maps a valid current user to the application', async () => {
  const setup = dependencies(user);
  const state = await loadCurrentUserSession(setup.value);
  assert.deepEqual(state, { status: 'authenticated', user });
  assert.equal(getCurrentUserDestination(state), 'application');
  assert.equal(setup.clearCount(), 0);
});

test('an active 401 clears the expired session exactly once and maps to the login redirect', async () => {
  const setup = dependencies(new ApiError('Unauthorized', 'http', 401));
  const states = [];
  const coordinator = createCurrentUserSessionRequestCoordinator((state) => states.push(state));
  const request = coordinator.begin();
  const state = await loadCurrentUserSession(setup.value, request.isActive);
  request.apply(state);
  assert.deepEqual(state, { status: 'anonymous', reason: 'expired-session' });
  assert.equal(getCurrentUserDestination(state), 'login');
  assert.equal(setup.clearCount(), 1);
  assert.deepEqual(states, [state]);
});

test('a superseded 401 cannot clear a newer token or replace newer UI state', async () => {
  const stale = dependencies(new ApiError('Unauthorized', 'http', 401));
  const states = [];
  const coordinator = createCurrentUserSessionRequestCoordinator((state) => states.push(state));
  const staleRequest = coordinator.begin();
  const currentRequest = coordinator.begin();
  const currentState = { status: 'authenticated', user };

  currentRequest.apply(currentState);
  const staleState = await loadCurrentUserSession(stale.value, staleRequest.isActive);
  staleRequest.apply(staleState);

  assert.equal(stale.clearCount(), 0);
  assert.deepEqual(states, [currentState]);
});

test('logout invalidates pending requests before their 401 side effects or UI updates', async () => {
  let rejectRequest;
  let clearCount = 0;
  const pendingResponse = new Promise((_, reject) => { rejectRequest = reject; });
  const states = [];
  const coordinator = createCurrentUserSessionRequestCoordinator((state) => states.push(state));
  const pendingRequest = coordinator.begin();
  const result = loadCurrentUserSession({
    readToken: () => 'token',
    readCurrentUser: () => pendingResponse,
    clearSession: () => { clearCount += 1; },
  }, pendingRequest.isActive);

  coordinator.invalidate();
  rejectRequest(new ApiError('Unauthorized', 'http', 401));
  pendingRequest.apply(await result);

  assert.equal(pendingRequest.isActive(), false);
  assert.equal(clearCount, 0);
  assert.deepEqual(states, []);
});

test('403 preserves the session and renders authorization-specific status', async () => {
  const setup = dependencies(new ApiError('Forbidden', 'http', 403));
  const state = await loadCurrentUserSession(setup.value);
  assert.deepEqual(state, { status: 'error', failure: 'forbidden' });
  assert.equal(getCurrentUserDestination(state), 'error');
  assert.equal(setup.clearCount(), 0);
  assert.deepEqual(getCurrentUserErrorView('forbidden'), {
    title: 'Доступ заборонено',
    message: 'Ваш обліковий запис не має дозволу на отримання даних поточної сесії.',
  });
});

test('malformed, network, server, configuration, and unexpected failures remain distinct without logout', async () => {
  const cases = [
    [new InvalidUserResponseError(), 'malformed-response'],
    [new ApiError('Network', 'network'), 'network'],
    [new ApiError('Server', 'http', 503), 'server'],
    [new ApiConfigurationError(), 'configuration'],
    [new ApiError('Conflict', 'http', 409), 'unexpected'],
    [new Error('Unknown'), 'unexpected'],
  ];

  for (const [error, failure] of cases) {
    const setup = dependencies(error);
    assert.deepEqual(await loadCurrentUserSession(setup.value), { status: 'error', failure });
    assert.equal(setup.clearCount(), 0);
    assert.notEqual(getCurrentUserErrorView(failure).title, '');
  }
});
