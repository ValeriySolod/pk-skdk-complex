import { useCallback, useEffect, useRef, useState } from 'react';
import { Button, EmptyState, Loader, PageHeader } from '../../shared/ui';
import { createUsersPageCoordinator, type UsersPageCoordinator } from './usersPageCoordinator.ts';
import { usersErrorMessages, type UsersState } from './usersState.ts';
import { createProfilesPageCoordinator, type ProfilesPageCoordinator } from './profilesPageCoordinator.ts';
import { profilesErrorMessages, type ProfilesState } from './profilesState.ts';
import styles from './AdminPage.module.css';

export function AdminPage() {
  const [state, setState] = useState<UsersState>({ status: 'loading' });
  const [profilesState, setProfilesState] = useState<ProfilesState>({ status: 'loading' });
  const coordinator = useRef<UsersPageCoordinator | null>(null);
  if (coordinator.current === null) {
    coordinator.current = createUsersPageCoordinator({
      applyState: setState,
      navigateToLogin: () => window.location.assign('/login'),
    });
  }
  const profilesCoordinator = useRef<ProfilesPageCoordinator | null>(null);
  if (profilesCoordinator.current === null) {
    profilesCoordinator.current = createProfilesPageCoordinator({ applyState: setProfilesState, navigateToLogin: () => window.location.assign('/login') });
  }
  const load = useCallback(async () => { await coordinator.current?.load(); }, []);
  const loadProfiles = useCallback(async () => { await profilesCoordinator.current?.load(); }, []);
  useEffect(() => {
    void load();
    void loadProfiles();
    return () => { coordinator.current?.invalidate(); profilesCoordinator.current?.invalidate(); };
  }, [load, loadProfiles]);

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
      <section className={styles.section} aria-labelledby="profiles-heading">
        <h2 id="profiles-heading">Profiles</h2>
        {profilesState.status === 'loading' && <div className={styles.status} role="status" aria-live="polite"><Loader /><span>Loading profiles...</span></div>}
        {profilesState.status === 'error' && <div className={styles.errorPanel} role="alert"><p>{profilesErrorMessages[profilesState.failure]}</p><Button type="button" onClick={() => void loadProfiles()}>Retry profiles</Button></div>}
        {profilesState.status === 'success' && profilesState.profiles.length === 0 && <EmptyState title="No profiles found" />}
        {profilesState.status === 'success' && profilesState.profiles.length > 0 && <div className={styles.tableWrap}><table className={styles.table}><thead><tr><th>ID</th><th>User ID</th><th>Display name</th><th>Personnel number</th><th>Job title</th><th>Phone</th><th>Status</th><th>Notes</th><th>Created</th><th>Updated</th></tr></thead><tbody>{profilesState.profiles.map((profile) => <tr key={profile.id}><td>{profile.id}</td><td>{profile.user_id}</td><td>{profile.display_name ?? '—'}</td><td>{profile.personnel_number ?? '—'}</td><td>{profile.job_title ?? '—'}</td><td>{profile.phone_number ?? '—'}</td><td>{profile.is_active ? 'Active' : 'Inactive'}</td><td>{profile.notes ?? '—'}</td><td>{profile.created_at}</td><td>{profile.updated_at}</td></tr>)}</tbody></table></div>}
      </section>
    </div>
  );
}
