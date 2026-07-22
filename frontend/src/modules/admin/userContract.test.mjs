import test from 'node:test';
import assert from 'node:assert/strict';
import { InvalidUsersResponseError, parseUsers } from './userContract.ts';

const validUser = { id: 7, username: 'operator', email: null, is_active: true };

test('UserRead list validation preserves the exact backend contract', () => {
  assert.deepEqual(parseUsers([validUser, { ...validUser, id: 8, email: 'user@example.test', is_active: false }]), [
    validUser,
    { ...validUser, id: 8, email: 'user@example.test', is_active: false },
  ]);
  assert.deepEqual(parseUsers([]), []);
});

test('UserRead validation rejects missing, mistyped, and additional fields', () => {
  const { email: _omitted, ...missingEmail } = validUser;
  for (const value of [null, {}, [null], [missingEmail], [{ ...validUser, id: 1.5 }], [{ ...validUser, username: 4 }], [{ ...validUser, email: 4 }], [{ ...validUser, is_active: 'true' }], [{ ...validUser, role: 'admin' }]]) {
    assert.throws(() => parseUsers(value), InvalidUsersResponseError);
  }
});
