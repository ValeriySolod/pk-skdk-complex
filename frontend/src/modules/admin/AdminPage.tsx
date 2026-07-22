import { useCallback, useEffect, useRef, useState } from 'react';
import { Button, EmptyState, Loader, PageHeader } from '../../shared/ui';
import { createUsersPageCoordinator, type UsersPageCoordinator } from './usersPageCoordinator.ts';
import { usersErrorMessages, type UsersState } from './usersState.ts';
import styles from './AdminPage.module.css';

export function AdminPage() {
  const [state, setState] = useState<UsersState>({ status: 'loading' });
  const coordinator = useRef<UsersPageCoordinator | null>(null);
  if (coordinator.current === null) {
    coordinator.current = createUsersPageCoordinator({
      applyState: setState,
      navigateToLogin: () => window.location.assign('/login'),
    });
  }
  const load = useCallback(async () => { await coordinator.current?.load(); }, []);
  useEffect(() => {
    void load();
    return () => coordinator.current?.invalidate();
  }, [load]);

  return (
    <div className={styles.page}>
      <PageHeader title="User management" description="Read-only users from the backend" />
      {state.status === 'loading' && <div className={styles.status} role="status" aria-live="polite"><Loader /><span>Loading users...</span></div>}
      {state.status === 'error' && <div className={styles.errorPanel} role="alert"><p>{usersErrorMessages[state.failure]}</p><Button type="button" onClick={() => void load()}>Retry</Button></div>}
      {state.status === 'success' && state.users.length === 0 && <EmptyState title="No users found" />}
      {state.status === 'success' && state.users.length > 0 && (
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead><tr><th>ID</th><th>Username</th><th>Email</th><th>Status</th></tr></thead>
            <tbody>{state.users.map((user) => <tr key={user.id}><td>{user.id}</td><td>{user.username}</td><td>{user.email ?? '—'}</td><td>{user.is_active ? 'Active' : 'Inactive'}</td></tr>)}</tbody>
          </table>
        </div>
      )}
    </div>
  );
}
