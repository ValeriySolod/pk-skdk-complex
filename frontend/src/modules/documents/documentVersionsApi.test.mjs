import test from 'node:test';
import assert from 'node:assert/strict';
import { getDemoDocumentVersions, getDocumentVersions, getRealDocumentVersions } from './documentVersionsApi.ts';

const versions = [{ id: 1, document_id: 7, version: '1.0', file_name: 'policy.pdf', storage_path: '/documents/policy.pdf', checksum: null, uploaded_by: null, uploaded_at: '2026-01-01T00:00:00Z' }];

test('real document versions loader uses the selected canonical endpoint and validates the response', async () => {
  let path;
  assert.deepEqual(await getRealDocumentVersions(7, async (value) => { path = value; return versions; }), versions);
  assert.equal(path, '/document-management/documents/7/versions');
});

test('demo document versions are detached and isolated from the real request path', async () => {
  const first = await getDemoDocumentVersions(1); first[0].version = 'changed';
  assert.notEqual((await getDemoDocumentVersions(1))[0].version, 'changed');
  let calls = 0;
  assert.deepEqual(await getDocumentVersions(7, { demoMode: true, request: async () => { calls += 1; return []; }, readDemoDocumentVersions: async () => versions }), versions);
  assert.equal(calls, 0);
  assert.deepEqual(await getDocumentVersions(7, { demoMode: false, request: async () => { calls += 1; return versions; }, readDemoDocumentVersions: async () => [] }), versions);
  assert.equal(calls, 1);
});
