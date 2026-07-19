import { loadOrganizationUnits, type OrganizationUnitsState } from './organizationUnitsState.ts';

export type OrganizationUnitsPageLoad = (
  isRequestActive: () => boolean,
) => Promise<OrganizationUnitsState>;

export type OrganizationUnitsPageCoordinatorDependencies = {
  applyState: (state: OrganizationUnitsState) => void;
  navigateToLogin: () => void;
  loadState?: OrganizationUnitsPageLoad;
};

export type OrganizationUnitsPageCoordinator = {
  load: () => Promise<void>;
  invalidate: () => void;
};

export function createOrganizationUnitsPageCoordinator({
  applyState,
  navigateToLogin,
  loadState = (isRequestActive) => loadOrganizationUnits(undefined, isRequestActive),
}: OrganizationUnitsPageCoordinatorDependencies): OrganizationUnitsPageCoordinator {
  let activeGeneration = 0;

  return {
    load: async () => {
      const generation = ++activeGeneration;
      const isRequestActive = () => generation === activeGeneration;
      applyState({ status: 'loading' });
      const state = await loadState(isRequestActive);
      if (!isRequestActive()) return;
      if (state.status === 'expired-session') {
        navigateToLogin();
        return;
      }
      applyState(state);
    },
    invalidate: () => { activeGeneration += 1; },
  };
}
