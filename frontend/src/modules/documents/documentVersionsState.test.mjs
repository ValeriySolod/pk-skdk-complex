import test from 'node:test';
import assert from 'node:assert/strict';
import { ApiConfigurationError, ApiError } from '../../api/client.ts';
import { InvalidDocumentVersionsResponseError } from './documentVersionContract.ts';
import { documentVersionsErrorMessages, loadDocumentVersions } from './documentVersionsState.ts';

function setup(result) {
  let clears = 0;
  return { dependencies: { readDocumentVersions: async () => { if (result instanceof Error) throw result; return result; }, clearSession: () => { clears += 1; } }, clears: () => clears };
}

test('document versions state represents populated and empty success for the selected document', async () => {
  assert.deepEqual(await loadDocumentVersions(7, setup([{ id: 1 }]).dependencies), { status: 'success', documentId: 7, versions: [{ id: 1 }] });
  assert.deepEqual(await loadDocumentVersions(8, setup([]).dependencies), { status: 'success', documentId: 8, versions: [] });
});

test('only an active document versions 401 clears the session', async () => {
  const active = setup(new ApiError('Unauthorized', 'http', 401));
  assert.deepEqual(await loadDocumentVersions(7, active.dependencies), { status: 'expired-session', documentId: 7 });
  assert.equal(active.clears(), 1);
  const stale = setup(new ApiError('Unauthorized', 'http', 401));
  await loadDocumentVersions(7, stale.dependencies, () => false);
  assert.equal(stale.clears(), 0);
});

test('document versions failures are distinct and preserve the session', async () => {
  const cases = [[new ApiError('Forbidden', 'http', 403), 'forbidden'], [new InvalidDocumentVersionsResponseError(), 'malformed-response'], [new ApiError('Network', 'network'), 'network'], [new ApiConfigurationError(), 'configuration'], [new ApiError('Server', 'http', 503), 'server'], [new Error('Unknown'), 'unexpected']];
  for (const [error, failure] of cases) {
    const current = setup(error);
    assert.deepEqual(await loadDocumentVersions(7, current.dependencies), { status: 'error', documentId: 7, failure });
    assert.equal(current.clears(), 0);
    assert.ok(documentVersionsErrorMessages[failure]);
  }
});
