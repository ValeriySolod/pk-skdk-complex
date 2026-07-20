import test from 'node:test';
import assert from 'node:assert/strict';
import { InvalidEmployeeAssignmentsResponseError, parseEmployeeAssignments } from './employeeAssignmentContract.ts';

const validAssignment = {
  id: 7,
  user_id: 12,
  position_id: 3,
  start_date: '2026-01-31',
  end_date: null,
  is_active: true,
};

test('EmployeeAssignmentRead list validation preserves the exact backend contract', () => {
  assert.deepEqual(parseEmployeeAssignments([
    validAssignment,
    { ...validAssignment, id: 8, start_date: '0001-01-01', end_date: '2026-12-31' },
  ]), [
    validAssignment,
    { ...validAssignment, id: 8, start_date: '0001-01-01', end_date: '2026-12-31' },
  ]);
  assert.deepEqual(parseEmployeeAssignments([]), []);
});

test('EmployeeAssignmentRead validation rejects missing, mistyped, invalid, and additional fields', () => {
  const { end_date: _omitted, ...missingEndDate } = validAssignment;
  const malformedValues = [
    null,
    {},
    [null],
    [missingEndDate],
    [{ ...validAssignment, id: 1.5 }],
    [{ ...validAssignment, user_id: '12' }],
    [{ ...validAssignment, position_id: null }],
    [{ ...validAssignment, start_date: 20260131 }],
    [{ ...validAssignment, start_date: '0000-01-01' }],
    [{ ...validAssignment, start_date: '2026-02-29' }],
    [{ ...validAssignment, end_date: '31-12-2026' }],
    [{ ...validAssignment, is_active: 'true' }],
    [{ ...validAssignment, unexpected: true }],
  ];
  for (const value of malformedValues) {
    assert.throws(() => parseEmployeeAssignments(value), InvalidEmployeeAssignmentsResponseError);
  }
});
