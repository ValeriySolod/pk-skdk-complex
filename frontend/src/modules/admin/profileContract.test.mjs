import test from 'node:test';
import assert from 'node:assert/strict';
import { InvalidProfilesResponseError, parseProfiles } from './profileContract.ts';

const validProfile = { id: 7, user_id: 3, display_name: null, personnel_number: 'PN-3', job_title: null, phone_number: '+3801', is_active: true, notes: null, created_at: '2026-07-22T10:11:12.123456+03:00', updated_at: '2026-07-22T07:11:12Z' };

test('UserManagementProfileRead list validation preserves the exact nullable backend contract', () => {
  assert.deepEqual(parseProfiles([validProfile, { ...validProfile, id: 8, display_name: 'Operator', personnel_number: null, job_title: 'Clerk', phone_number: null, is_active: false, notes: 'Archived', created_at: '2026-01-01T00:00:00' }]), [validProfile, { ...validProfile, id: 8, display_name: 'Operator', personnel_number: null, job_title: 'Clerk', phone_number: null, is_active: false, notes: 'Archived', created_at: '2026-01-01T00:00:00' }]);
  assert.deepEqual(parseProfiles([]), []);
});

test('UserManagementProfileRead validation rejects missing, mistyped, additional, and invalid datetime fields', () => {
  const { notes: _omitted, ...missingNotes } = validProfile;
  for (const value of [null, {}, [null], [missingNotes], [{ ...validProfile, id: 1.5 }], [{ ...validProfile, user_id: '3' }], [{ ...validProfile, display_name: 4 }], [{ ...validProfile, personnel_number: false }], [{ ...validProfile, job_title: [] }], [{ ...validProfile, phone_number: 1 }], [{ ...validProfile, is_active: 'true' }], [{ ...validProfile, notes: {} }], [{ ...validProfile, created_at: '2026-02-30T00:00:00Z' }], [{ ...validProfile, updated_at: 'not-a-datetime' }], [{ ...validProfile, role: 'admin' }]]) assert.throws(() => parseProfiles(value), InvalidProfilesResponseError);
});
