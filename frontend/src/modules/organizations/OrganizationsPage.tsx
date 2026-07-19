import { useCallback, useEffect, useRef, useState } from 'react';
import { Button, EmptyState, Loader, PageHeader } from '../../shared/ui';
import { createOrganizationUnitsPageCoordinator, type OrganizationUnitsPageCoordinator } from './organizationUnitsPageCoordinator.ts';
import { organizationUnitsErrorMessages, type OrganizationUnitsState } from './organizationUnitsState.ts';
import styles from './OrganizationsPage.module.css';

export function OrganizationsPage() {
  const [state, setState] = useState<OrganizationUnitsState>({ status: 'loading' });
  const coordinator = useRef<OrganizationUnitsPageCoordinator | null>(null);
  if (coordinator.current === null) {
    coordinator.current = createOrganizationUnitsPageCoordinator({
      applyState: setState,
      navigateToLogin: () => window.location.assign('/login'),
    });
  }

  const load = useCallback(async () => {
    await coordinator.current?.load();
  }, []);

  useEffect(() => {
    void load();
    return () => coordinator.current?.invalidate();
  }, [load]);

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
    </div>
  );
}
