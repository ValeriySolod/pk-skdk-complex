import test from 'node:test';
import assert from 'node:assert/strict';
import { InvalidDocumentCategoriesResponseError, parseDocumentCategories } from './documentCategoryContract.ts';

const valid = { id: 1, name: 'Policies', code: 'POLICY', description: 'Policy documents', is_active: true };

test('DocumentCategoryRead validation accepts the exact list contract and nullable description', () => {
  assert.deepEqual(parseDocumentCategories([valid, { ...valid, id: 2, description: null, is_active: false }]), [valid, { ...valid, id: 2, description: null, is_active: false }]);
  assert.deepEqual(parseDocumentCategories([]), []);
});

test('DocumentCategoryRead validation rejects missing, mistyped, and additional fields', () => {
  const { description: _omitted, ...missing } = valid;
  for (const value of [null, {}, [missing], [{ ...valid, id: 1.5 }], [{ ...valid, name: 1 }], [{ ...valid, code: null }], [{ ...valid, description: 2 }], [{ ...valid, is_active: 1 }], [{ ...valid, extra: true }]]) {
    assert.throws(() => parseDocumentCategories(value), InvalidDocumentCategoriesResponseError);
  }
});
