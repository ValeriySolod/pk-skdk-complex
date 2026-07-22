import test from 'node:test';
import assert from 'node:assert/strict';
import { InvalidRoleAssignmentsResponseError, parseRoleAssignments } from './roleAssignmentContract.ts';

const validAssignment = { id: 7, user_id: 3, role_code: 'audit.reader', scope_type: null, scope_id: null, is_active: true, assigned_by_user_id: null, assigned_at: '2026-07-22T10:11:12.123456+03:00', revoked_at: null };
test('UserManagementRoleAssignmentRead list validation preserves the exact nullable backend contract', () => {
  const revoked = { ...validAssignment, id: 8, scope_type: 'department', scope_id: 4, is_active: false, assigned_by_user_id: 2, assigned_at: '2026-01-01T00:00:00', revoked_at: '2026-02-01T00:00:00Z' };
  assert.deepEqual(parseRoleAssignments([validAssignment, revoked]), [validAssignment, revoked]);
  assert.deepEqual(parseRoleAssignments([]), []);
});
test('UserManagementRoleAssignmentRead validation rejects missing, mistyped, additional, and invalid datetime fields', () => {
  const { revoked_at: _omitted, ...missingRevokedAt } = validAssignment;
  for (const value of [null, {}, [null], [missingRevokedAt], [{ ...validAssignment, id: 1.5 }], [{ ...validAssignment, user_id: '3' }], [{ ...validAssignment, role_code: 4 }], [{ ...validAssignment, scope_type: 4 }], [{ ...validAssignment, scope_id: '4' }], [{ ...validAssignment, is_active: 'true' }], [{ ...validAssignment, assigned_by_user_id: false }], [{ ...validAssignment, assigned_at: '2026-02-30T00:00:00Z' }], [{ ...validAssignment, revoked_at: 'not-a-datetime' }], [{ ...validAssignment, extra: true }]]) assert.throws(() => parseRoleAssignments(value), InvalidRoleAssignmentsResponseError);
});
