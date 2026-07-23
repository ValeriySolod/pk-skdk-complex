import test from 'node:test';
import assert from 'node:assert/strict';
import { InvalidDocumentsResponseError, parseDocuments } from './documentContract.ts';
const valid = { id: 1, title: 'Policy', document_number: null, description: null, document_type: 'policy', status: 'active', organization_id: null, owner_user_id: 2, created_at: '2026-07-23T10:11:12.123456+03:00', updated_at: '2026-07-23T07:11:12Z' };
test('DocumentRead validation accepts the exact backend list contract and nullable fields', () => { assert.deepEqual(parseDocuments([valid]), [valid]); assert.deepEqual(parseDocuments([]), []); });
test('DocumentRead validation rejects missing, mistyped, additional, and invalid datetime fields', () => {
  const { description: _omitted, ...missing } = valid;
  for (const value of [null, {}, [missing], [{ ...valid, id: 1.5 }], [{ ...valid, document_number: 2 }], [{ ...valid, organization_id: '1' }], [{ ...valid, created_at: '2026-02-30T00:00:00Z' }], [{ ...valid, extra: true }]]) assert.throws(() => parseDocuments(value), InvalidDocumentsResponseError);
});
