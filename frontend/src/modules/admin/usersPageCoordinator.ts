import { loadUsers, type UsersState } from './usersState.ts';

export type UsersPageLoad = (isRequestActive: () => boolean) => Promise<UsersState>;
export type UsersPageCoordinator = { load: () => Promise<void>; invalidate: () => void };

export function createUsersPageCoordinator({
  applyState,
  navigateToLogin,
  loadState = (isRequestActive) => loadUsers(undefined, isRequestActive),
}: {
  applyState: (state: UsersState) => void;
  navigateToLogin: () => void;
  loadState?: UsersPageLoad;
}): UsersPageCoordinator {
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
