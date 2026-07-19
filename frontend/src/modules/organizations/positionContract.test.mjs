import test from 'node:test';
import assert from 'node:assert/strict';
import { InvalidPositionsResponseError, parsePositions } from './positionContract.ts';

const validPosition = { id: 7, title: 'Inspector', code: 'INSP', organization_unit_id: 2, is_active: true };

test('PositionRead list validation preserves the exact backend contract', () => {
  assert.deepEqual(parsePositions([validPosition, { ...validPosition, id: 8, code: null }]), [
    validPosition,
    { ...validPosition, id: 8, code: null },
  ]);
  assert.deepEqual(parsePositions([]), []);
});

test('PositionRead validation rejects wrong containers, fields, types, and extra fields', () => {
  const malformedValues = [
    null,
    {},
    [null],
    [{ ...validPosition, id: 1.5 }],
    [{ ...validPosition, title: null }],
    [{ ...validPosition, code: undefined }],
    [{ ...validPosition, organization_unit_id: '2' }],
    [{ ...validPosition, is_active: 'true' }],
    [{ ...validPosition, unexpected: true }],
  ];
  for (const value of malformedValues) {
    assert.throws(() => parsePositions(value), InvalidPositionsResponseError);
  }
});
