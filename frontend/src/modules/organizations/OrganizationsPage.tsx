import { useCallback, useEffect, useRef, useState } from 'react';
import { Button, EmptyState, Loader, PageHeader } from '../../shared/ui';
import { createEmployeeAssignmentsPageCoordinator, type EmployeeAssignmentsPageCoordinator } from './employeeAssignmentsPageCoordinator.ts';
import { employeeAssignmentsErrorMessages, type EmployeeAssignmentsState } from './employeeAssignmentsState.ts';
import { createOrganizationUnitsPageCoordinator, type OrganizationUnitsPageCoordinator } from './organizationUnitsPageCoordinator.ts';
import { organizationUnitsErrorMessages, type OrganizationUnitsState } from './organizationUnitsState.ts';
import { createPositionsPageCoordinator, type PositionsPageCoordinator } from './positionsPageCoordinator.ts';
import { positionsErrorMessages, type PositionsState } from './positionsState.ts';
import styles from './OrganizationsPage.module.css';

export function OrganizationsPage() {
  const [state, setState] = useState<OrganizationUnitsState>({ status: 'loading' });
  const [positionsState, setPositionsState] = useState<PositionsState>({ status: 'loading' });
  const [employeeAssignmentsState, setEmployeeAssignmentsState] = useState<EmployeeAssignmentsState>({ status: 'loading' });
  const coordinator = useRef<OrganizationUnitsPageCoordinator | null>(null);
  if (coordinator.current === null) {
    coordinator.current = createOrganizationUnitsPageCoordinator({
      applyState: setState,
      navigateToLogin: () => window.location.assign('/login'),
    });
  }
  const positionsCoordinator = useRef<PositionsPageCoordinator | null>(null);
  if (positionsCoordinator.current === null) {
    positionsCoordinator.current = createPositionsPageCoordinator({
      applyState: setPositionsState,
      navigateToLogin: () => window.location.assign('/login'),
    });
  }
  const employeeAssignmentsCoordinator = useRef<EmployeeAssignmentsPageCoordinator | null>(null);
  if (employeeAssignmentsCoordinator.current === null) {
    employeeAssignmentsCoordinator.current = createEmployeeAssignmentsPageCoordinator({
      applyState: setEmployeeAssignmentsState,
      navigateToLogin: () => window.location.assign('/login'),
    });
  }

  const load = useCallback(async () => {
    await coordinator.current?.load();
  }, []);
  const loadPositions = useCallback(async () => {
    await positionsCoordinator.current?.load();
  }, []);
  const loadEmployeeAssignments = useCallback(async () => {
    await employeeAssignmentsCoordinator.current?.load();
  }, []);

  useEffect(() => {
    void load();
    void loadPositions();
    void loadEmployeeAssignments();
    return () => {
      coordinator.current?.invalidate();
      positionsCoordinator.current?.invalidate();
      employeeAssignmentsCoordinator.current?.invalidate();
    };
  }, [load, loadPositions, loadEmployeeAssignments]);

  return (
    <div className={styles.page}>
      <PageHeader
        title="Organization units"
        description="Read-only organization structure from the backend"
      />

      {state.status === 'loading' && (
        <div className={styles.status} role="status" aria-live="polite">
          <Loader />
          <span>Loading organization units...</span>
        </div>
      )}

      {state.status === 'error' && (
        <div className={styles.errorPanel} role="alert">
          <p>{organizationUnitsErrorMessages[state.failure]}</p>
          <Button type="button" onClick={() => void load()}>Retry</Button>
        </div>
      )}

      {state.status === 'success' && state.units.length === 0 && (
        <EmptyState title="No organization units found" />
      )}

      {state.status === 'success' && state.units.length > 0 && (
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead>
              <tr><th>ID</th><th>Name</th><th>Code</th><th>Parent ID</th><th>Status</th></tr>
            </thead>
            <tbody>
              {state.units.map((unit) => (
                <tr key={unit.id}>
                  <td>{unit.id}</td>
                  <td>{unit.name}</td>
                  <td>{unit.code ?? '—'}</td>
                  <td>{unit.parent_id ?? '—'}</td>
                  <td>{unit.is_active ? 'Active' : 'Inactive'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <section className={styles.section} aria-labelledby="positions-heading">
        <h2 id="positions-heading">Positions</h2>

        {positionsState.status === 'loading' && (
          <div className={styles.status} role="status" aria-live="polite">
            <Loader />
            <span>Loading positions...</span>
          </div>
        )}

        {positionsState.status === 'error' && (
          <div className={styles.errorPanel} role="alert">
            <p>{positionsErrorMessages[positionsState.failure]}</p>
            <Button type="button" onClick={() => void loadPositions()}>Retry positions</Button>
          </div>
        )}

        {positionsState.status === 'success' && positionsState.positions.length === 0 && (
          <EmptyState title="No positions found" />
        )}

        {positionsState.status === 'success' && positionsState.positions.length > 0 && (
          <div className={styles.tableWrap}>
            <table className={styles.table}>
              <thead>
                <tr><th>ID</th><th>Title</th><th>Code</th><th>Organization unit ID</th><th>Status</th></tr>
              </thead>
              <tbody>
                {positionsState.positions.map((position) => (
                  <tr key={position.id}>
                    <td>{position.id}</td>
                    <td>{position.title}</td>
                    <td>{position.code ?? '—'}</td>
                    <td>{position.organization_unit_id}</td>
                    <td>{position.is_active ? 'Active' : 'Inactive'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className={styles.section} aria-labelledby="employee-assignments-heading">
        <h2 id="employee-assignments-heading">Employee assignments</h2>

        {employeeAssignmentsState.status === 'loading' && (
          <div className={styles.status} role="status" aria-live="polite">
            <Loader />
            <span>Loading employee assignments...</span>
          </div>
        )}

        {employeeAssignmentsState.status === 'error' && (
          <div className={styles.errorPanel} role="alert">
            <p>{employeeAssignmentsErrorMessages[employeeAssignmentsState.failure]}</p>
            <Button type="button" onClick={() => void loadEmployeeAssignments()}>Retry employee assignments</Button>
          </div>
        )}

        {employeeAssignmentsState.status === 'success' && employeeAssignmentsState.assignments.length === 0 && (
          <EmptyState title="No employee assignments found" />
        )}

        {employeeAssignmentsState.status === 'success' && employeeAssignmentsState.assignments.length > 0 && (
          <div className={styles.tableWrap}>
            <table className={styles.table}>
              <thead>
                <tr><th>ID</th><th>User ID</th><th>Position ID</th><th>Start date</th><th>End date</th><th>Status</th></tr>
              </thead>
              <tbody>
                {employeeAssignmentsState.assignments.map((assignment) => (
                  <tr key={assignment.id}>
                    <td>{assignment.id}</td>
                    <td>{assignment.user_id}</td>
                    <td>{assignment.position_id}</td>
                    <td>{assignment.start_date ?? '—'}</td>
                    <td>{assignment.end_date ?? '—'}</td>
                    <td>{assignment.is_active ? 'Active' : 'Inactive'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
