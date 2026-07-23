import { loadDocuments, type DocumentsState } from './documentsState.ts';
export type DocumentsPageCoordinator = { load: () => Promise<void>; invalidate: () => void };
export function createDocumentsPageCoordinator({ applyState, navigateToLogin, loadState = (active) => loadDocuments(undefined, active) }: { applyState: (state: DocumentsState) => void; navigateToLogin: () => void; loadState?: (active: () => boolean) => Promise<DocumentsState> }): DocumentsPageCoordinator {
  let generation = 0;
  return { load: async () => { const current = ++generation; const active = () => current === generation; applyState({ status: 'loading' }); const state = await loadState(active); if (!active()) return; if (state.status === 'expired-session') { navigateToLogin(); return; } applyState(state); }, invalidate: () => { generation += 1; } };
}
