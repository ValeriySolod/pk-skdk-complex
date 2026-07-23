import test from 'node:test';
import assert from 'node:assert/strict';
import { InvalidDocumentVersionsResponseError, parseDocumentVersions } from './documentVersionContract.ts';

const valid = { id: 1, document_id: 2, version: '1.0', file_name: 'policy.pdf', storage_path: '/documents/policy.pdf', checksum: null, uploaded_by: null, uploaded_at: '2026-07-23T10:11:12.123456+03:00' };

test('DocumentVersionRead validation accepts the exact list contract and nullable fields', () => {
  assert.deepEqual(parseDocumentVersions([valid, { ...valid, id: 2, checksum: 'sha256:value', uploaded_by: 3 }]), [valid, { ...valid, id: 2, checksum: 'sha256:value', uploaded_by: 3 }]);
  assert.deepEqual(parseDocumentVersions([]), []);
});

test('DocumentVersionRead validation rejects missing, mistyped, additional, and invalid datetime fields', () => {
  const { checksum: _omitted, ...missing } = valid;
  for (const value of [null, {}, [missing], [{ ...valid, id: 1.5 }], [{ ...valid, document_id: '2' }], [{ ...valid, version: 1 }], [{ ...valid, checksum: 2 }], [{ ...valid, uploaded_by: '3' }], [{ ...valid, uploaded_at: '2026-02-30T00:00:00Z' }], [{ ...valid, extra: true }]]) {
    assert.throws(() => parseDocumentVersions(value), InvalidDocumentVersionsResponseError);
  }
});
