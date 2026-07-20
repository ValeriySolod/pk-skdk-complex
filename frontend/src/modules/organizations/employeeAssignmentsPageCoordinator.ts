import { loadEmployeeAssignments, type EmployeeAssignmentsState } from './employeeAssignmentsState.ts';

export type EmployeeAssignmentsPageLoad = (
  isRequestActive: () => boolean,
) => Promise<EmployeeAssignmentsState>;

export type EmployeeAssignmentsPageCoordinatorDependencies = {
  applyState: (state: EmployeeAssignmentsState) => void;
  navigateToLogin: () => void;
  loadState?: EmployeeAssignmentsPageLoad;
};

export type EmployeeAssignmentsPageCoordinator = {
  load: () => Promise<void>;
  invalidate: () => void;
};

export function createEmployeeAssignmentsPageCoordinator({
  applyState,
  navigateToLogin,
  loadState = (isRequestActive) => loadEmployeeAssignments(undefined, isRequestActive),
}: EmployeeAssignmentsPageCoordinatorDependencies): EmployeeAssignmentsPageCoordinator {
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
