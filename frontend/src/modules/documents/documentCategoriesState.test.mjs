import test from 'node:test';
import assert from 'node:assert/strict';
import { ApiConfigurationError, ApiError } from '../../api/client.ts';
import { InvalidDocumentCategoriesResponseError } from './documentCategoryContract.ts';
import { documentCategoriesErrorMessages, loadDocumentCategories } from './documentCategoriesState.ts';

function setup(result) {
  let clears = 0;
  return { dependencies: { readDocumentCategories: async () => { if (result instanceof Error) throw result; return result; }, clearSession: () => { clears += 1; } }, clears: () => clears };
}

test('document categories state represents populated and empty success', async () => {
  assert.deepEqual(await loadDocumentCategories(setup([{ id: 1 }]).dependencies), { status: 'success', categories: [{ id: 1 }] });
  assert.deepEqual(await loadDocumentCategories(setup([]).dependencies), { status: 'success', categories: [] });
});

test('only an active document categories 401 clears the session', async () => {
  const active = setup(new ApiError('Unauthorized', 'http', 401));
  assert.deepEqual(await loadDocumentCategories(active.dependencies), { status: 'expired-session' });
  assert.equal(active.clears(), 1);
  const stale = setup(new ApiError('Unauthorized', 'http', 401));
  await loadDocumentCategories(stale.dependencies, () => false);
  assert.equal(stale.clears(), 0);
});

test('document categories failures are distinct and preserve the session', async () => {
  const cases = [[new ApiError('Forbidden', 'http', 403), 'forbidden'], [new InvalidDocumentCategoriesResponseError(), 'malformed-response'], [new ApiError('Network', 'network'), 'network'], [new ApiConfigurationError(), 'configuration'], [new ApiError('Server', 'http', 503), 'server'], [new Error('Unknown'), 'unexpected']];
  for (const [error, failure] of cases) {
    const current = setup(error);
    assert.deepEqual(await loadDocumentCategories(current.dependencies), { status: 'error', failure });
    assert.equal(current.clears(), 0);
    assert.ok(documentCategoriesErrorMessages[failure]);
  }
});
