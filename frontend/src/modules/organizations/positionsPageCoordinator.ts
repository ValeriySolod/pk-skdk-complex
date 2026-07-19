import { loadPositions, type PositionsState } from './positionsState.ts';

export type PositionsPageLoad = (
  isRequestActive: () => boolean,
) => Promise<PositionsState>;

export type PositionsPageCoordinatorDependencies = {
  applyState: (state: PositionsState) => void;
  navigateToLogin: () => void;
  loadState?: PositionsPageLoad;
};

export type PositionsPageCoordinator = {
  load: () => Promise<void>;
  invalidate: () => void;
};

export function createPositionsPageCoordinator({
  applyState,
  navigateToLogin,
  loadState = (isRequestActive) => loadPositions(undefined, isRequestActive),
}: PositionsPageCoordinatorDependencies): PositionsPageCoordinator {
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
