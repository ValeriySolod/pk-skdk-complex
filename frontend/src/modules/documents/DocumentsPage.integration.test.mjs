import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
test('registered documents page wires the coordinator and shared loading, empty, table, and error UI', async () => {
  const [page, registry] = await Promise.all([readFile(new URL('./DocumentsPage.tsx', import.meta.url), 'utf8'), readFile(new URL('../../app/moduleRegistry.tsx', import.meta.url), 'utf8')]);
  for (const marker of ['createDocumentsPageCoordinator', 'Loading documents...', 'No documents found', '<Table', 'documentsErrorMessages']) assert.match(page, new RegExp(marker.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
  assert.match(registry, /id: 'documents'[\s\S]*path: '\/documents'[\s\S]*Component: DocumentsPage/);
});
