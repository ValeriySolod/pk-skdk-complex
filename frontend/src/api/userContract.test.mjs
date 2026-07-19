import test from 'node:test';
import assert from 'node:assert/strict';
import { InvalidUserResponseError, parseUser } from './userContract.ts';

const validUser = {
  id: 17,
  username: 'operator',
  full_name: 'Олена Коваль',
  role: 'OPERATOR',
  department: null,
  is_active: true,
};

test('UserRead validation accepts and preserves every canonical field', () => {
  assert.deepEqual(parseUser(validUser), validUser);
  assert.deepEqual(parseUser({ ...validUser, department: 'Канцелярія' }), {
    ...validUser,
    department: 'Канцелярія',
  });
});

test('UserRead validation rejects malformed successful responses', () => {
  const malformedValues = [
    null,
    {},
    { ...validUser, id: 1.5 },
    { ...validUser, username: null },
    { ...validUser, full_name: undefined },
    { ...validUser, role: 2 },
    { ...validUser, department: undefined },
    { ...validUser, is_active: 'true' },
  ];

  for (const value of malformedValues) {
    assert.throws(() => parseUser(value), InvalidUserResponseError);
  }
});
