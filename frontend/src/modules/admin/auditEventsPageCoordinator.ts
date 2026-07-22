import { loadAuditEvents, type AuditEventsState } from './auditEventsState.ts';

export type AuditEventsPageLoad = (isRequestActive: () => boolean) => Promise<AuditEventsState>;
export type AuditEventsPageCoordinator = { load: () => Promise<void>; invalidate: () => void };
export function createAuditEventsPageCoordinator({ applyState, navigateToLogin, loadState = (isRequestActive) => loadAuditEvents(undefined, isRequestActive) }: { applyState: (state: AuditEventsState) => void; navigateToLogin: () => void; loadState?: AuditEventsPageLoad }): AuditEventsPageCoordinator {
  let activeGeneration = 0;
  return {
    load: async () => {
      const generation = ++activeGeneration;
      const isRequestActive = () => generation === activeGeneration;
      applyState({ status: 'loading' });
      const state = await loadState(isRequestActive);
      if (!isRequestActive()) return;
      if (state.status === 'expired-session') { navigateToLogin(); return; }
      applyState(state);
    },
    invalidate: () => { activeGeneration += 1; },
  };
}
