import test from 'node:test';
import assert from 'node:assert/strict';
import { getDemoDocumentCategories, getDocumentCategories, getRealDocumentCategories } from './documentCategoriesApi.ts';

const categories = [{ id: 1, name: 'Policies', code: 'POLICY', description: null, is_active: true }];

test('real document categories loader uses the canonical endpoint and validates the response', async () => {
  let path;
  assert.deepEqual(await getRealDocumentCategories(async (value) => { path = value; return categories; }), categories);
  assert.equal(path, '/document-management/categories');
});

test('demo document categories are detached and isolated from the real request path', async () => {
  const first = await getDemoDocumentCategories(); first[0].name = 'Changed';
  assert.notEqual((await getDemoDocumentCategories())[0].name, 'Changed');
  let calls = 0;
  assert.deepEqual(await getDocumentCategories({ demoMode: true, request: async () => { calls += 1; return []; }, readDemoDocumentCategories: async () => categories }), categories);
  assert.equal(calls, 0);
  assert.deepEqual(await getDocumentCategories({ demoMode: false, request: async () => { calls += 1; return categories; }, readDemoDocumentCategories: async () => [] }), categories);
  assert.equal(calls, 1);
});
