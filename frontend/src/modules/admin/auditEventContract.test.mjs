import test from 'node:test';
import assert from 'node:assert/strict';
import { InvalidAuditEventsResponseError, parseAuditEvents } from './auditEventContract.ts';

const validEvent = { id: 7, actor_user_id: null, target_user_id: null, event_type: 'profile.created', summary: null, details: null, created_at: '2026-07-22T10:11:12.123456+03:00' };
test('UserManagementAuditEventRead list validation preserves the exact nullable and nested backend contract', () => {
  const detailed = { ...validEvent, id: 8, actor_user_id: 2, target_user_id: 3, summary: 'Role assigned', details: { role: 'audit.reader', context: { source: 'admin' }, changes: [1, true, null] }, created_at: '2026-01-01T00:00:00Z' };
  assert.deepEqual(parseAuditEvents([validEvent, detailed]), [validEvent, detailed]);
  assert.deepEqual(parseAuditEvents([]), []);
});
test('UserManagementAuditEventRead validation rejects missing, mistyped, additional, invalid datetime, array, and non-plain details values', () => {
  const { summary: _omitted, ...missingSummary } = validEvent;
  class Details {}
  for (const value of [null, {}, [null], [missingSummary], [{ ...validEvent, id: 1.5 }], [{ ...validEvent, actor_user_id: '2' }], [{ ...validEvent, target_user_id: false }], [{ ...validEvent, event_type: 4 }], [{ ...validEvent, summary: 4 }], [{ ...validEvent, details: [] }], [{ ...validEvent, details: new Details() }], [{ ...validEvent, created_at: '2026-02-30T00:00:00Z' }], [{ ...validEvent, extra: true }]]) assert.throws(() => parseAuditEvents(value), InvalidAuditEventsResponseError);
});
