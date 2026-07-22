import test from 'node:test';
import assert from 'node:assert/strict';
import { ApiConfigurationError, ApiError } from '../../api/client.ts';
import { InvalidAuditEventsResponseError } from './auditEventContract.ts';
import { auditEventsErrorMessages, loadAuditEvents } from './auditEventsState.ts';

const auditEvents = [{ id: 1 }];
function dependencies(result) { let clearCount = 0; return { value: { readAuditEvents: async () => { if (result instanceof Error) throw result; return result; }, clearSession: () => { clearCount += 1; } }, clearCount: () => clearCount }; }
test('audit events orchestration represents populated and empty success deterministically', async () => { assert.deepEqual(await loadAuditEvents(dependencies(auditEvents).value), { status: 'success', auditEvents }); assert.deepEqual(await loadAuditEvents(dependencies([]).value), { status: 'success', auditEvents: [] }); });
test('active audit events 401 expires the session while stale 401 has no token side effect', async () => { const active = dependencies(new ApiError('Unauthorized', 'http', 401)); assert.deepEqual(await loadAuditEvents(active.value), { status: 'expired-session' }); assert.equal(active.clearCount(), 1); const stale = dependencies(new ApiError('Unauthorized', 'http', 401)); assert.deepEqual(await loadAuditEvents(stale.value, () => false), { status: 'expired-session' }); assert.equal(stale.clearCount(), 0); });
test('403 and all other audit events failures remain distinct and preserve the token', async () => { const cases = [[new ApiError('Forbidden', 'http', 403), 'forbidden'], [new InvalidAuditEventsResponseError(), 'malformed-response'], [new ApiError('Network', 'network'), 'network'], [new ApiConfigurationError(), 'configuration'], [new ApiError('Server', 'http', 503), 'server'], [new ApiError('Conflict', 'http', 409), 'unexpected'], [new Error('Unknown'), 'unexpected']]; for (const [error, failure] of cases) { const setup = dependencies(error); assert.deepEqual(await loadAuditEvents(setup.value), { status: 'error', failure }); assert.equal(setup.clearCount(), 0); assert.notEqual(auditEventsErrorMessages[failure], ''); } });
