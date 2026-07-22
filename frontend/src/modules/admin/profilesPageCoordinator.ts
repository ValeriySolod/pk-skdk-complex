import { loadProfiles, type ProfilesState } from './profilesState.ts';

export type ProfilesPageLoad = (isRequestActive: () => boolean) => Promise<ProfilesState>;
export type ProfilesPageCoordinator = { load: () => Promise<void>; invalidate: () => void };
export function createProfilesPageCoordinator({ applyState, navigateToLogin, loadState = (isRequestActive) => loadProfiles(undefined, isRequestActive) }: {
  applyState: (state: ProfilesState) => void; navigateToLogin: () => void; loadState?: ProfilesPageLoad;
}): ProfilesPageCoordinator {
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
