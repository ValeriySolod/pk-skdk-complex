import { loadDocumentVersions, type DocumentVersionsState } from './documentVersionsState.ts';

export type DocumentVersionsPageLoad = (documentId: number, isRequestActive: () => boolean) => Promise<DocumentVersionsState>;
export type DocumentVersionsPageCoordinator = {
  load: (documentId: number) => Promise<void>;
  clear: () => void;
  invalidate: () => void;
};

export function createDocumentVersionsPageCoordinator({
  applyState,
  navigateToLogin,
  loadState = (documentId, isRequestActive) => loadDocumentVersions(documentId, undefined, isRequestActive),
}: {
  applyState: (state: DocumentVersionsState) => void;
  navigateToLogin: () => void;
  loadState?: DocumentVersionsPageLoad;
}): DocumentVersionsPageCoordinator {
  let activeGeneration = 0;
  return {
    load: async (documentId) => {
      const generation = ++activeGeneration;
      const isRequestActive = () => generation === activeGeneration;
      applyState({ status: 'loading', documentId });
      const state = await loadState(documentId, isRequestActive);
      if (!isRequestActive()) return;
      if (state.status === 'expired-session') { navigateToLogin(); return; }
      applyState(state);
    },
    clear: () => { activeGeneration += 1; applyState({ status: 'unselected' }); },
    invalidate: () => { activeGeneration += 1; },
  };
}
