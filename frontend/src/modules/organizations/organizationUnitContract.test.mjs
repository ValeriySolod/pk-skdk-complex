import test from 'node:test';
import assert from 'node:assert/strict';
import { InvalidOrganizationUnitsResponseError, parseOrganizationUnits } from './organizationUnitContract.ts';

const validUnit = { id: 7, name: 'Operations', code: 'OPS', parent_id: null, is_active: true };

test('OrganizationUnitRead list validation preserves the exact backend contract', () => {
  assert.deepEqual(parseOrganizationUnits([validUnit, { ...validUnit, id: 8, code: null, parent_id: 7 }]), [
    validUnit,
    { ...validUnit, id: 8, code: null, parent_id: 7 },
  ]);
  assert.deepEqual(parseOrganizationUnits([]), []);
});

test('OrganizationUnitRead validation rejects wrong containers, fields, types, and extra fields', () => {
  const malformedValues = [
    null,
    {},
    [null],
    [{ ...validUnit, id: 1.5 }],
    [{ ...validUnit, name: null }],
    [{ ...validUnit, code: undefined }],
    [{ ...validUnit, parent_id: '7' }],
    [{ ...validUnit, is_active: 'true' }],
    [{ ...validUnit, unexpected: true }],
  ];
  for (const value of malformedValues) {
    assert.throws(() => parseOrganizationUnits(value), InvalidOrganizationUnitsResponseError);
  }
});
