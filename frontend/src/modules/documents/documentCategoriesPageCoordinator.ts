import { loadDocumentCategories, type DocumentCategoriesState } from './documentCategoriesState.ts';

export type DocumentCategoriesPageCoordinator = { load: () => Promise<void>; invalidate: () => void };

export function createDocumentCategoriesPageCoordinator({
  applyState,
  navigateToLogin,
  loadState = (active) => loadDocumentCategories(undefined, active),
}: {
  applyState: (state: DocumentCategoriesState) => void;
  navigateToLogin: () => void;
  loadState?: (active: () => boolean) => Promise<DocumentCategoriesState>;
}): DocumentCategoriesPageCoordinator {
  let generation = 0;
  return {
    load: async () => {
      const current = ++generation;
      const active = () => current === generation;
      applyState({ status: 'loading' });
      const state = await loadState(active);
      if (!active()) return;
      if (state.status === 'expired-session') { navigateToLogin(); return; }
      applyState(state);
    },
    invalidate: () => { generation += 1; },
  };
}
