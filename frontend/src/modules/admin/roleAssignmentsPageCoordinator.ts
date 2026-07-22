import { loadRoleAssignments, type RoleAssignmentsState } from './roleAssignmentsState.ts';

export type RoleAssignmentsPageLoad = (isRequestActive: () => boolean) => Promise<RoleAssignmentsState>;
export type RoleAssignmentsPageCoordinator = { load: () => Promise<void>; invalidate: () => void };
export function createRoleAssignmentsPageCoordinator({ applyState, navigateToLogin, loadState = (isRequestActive) => loadRoleAssignments(undefined, isRequestActive) }: { applyState: (state: RoleAssignmentsState) => void; navigateToLogin: () => void; loadState?: RoleAssignmentsPageLoad }): RoleAssignmentsPageCoordinator {
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
