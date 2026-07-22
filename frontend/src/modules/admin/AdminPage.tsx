import { useCallback, useEffect, useRef, useState } from 'react';
import { Button, EmptyState, Loader, PageHeader } from '../../shared/ui';
import { createUsersPageCoordinator, type UsersPageCoordinator } from './usersPageCoordinator.ts';
import { usersErrorMessages, type UsersState } from './usersState.ts';
import { createProfilesPageCoordinator, type ProfilesPageCoordinator } from './profilesPageCoordinator.ts';
import { profilesErrorMessages, type ProfilesState } from './profilesState.ts';
import { createRoleAssignmentsPageCoordinator, type RoleAssignmentsPageCoordinator } from './roleAssignmentsPageCoordinator.ts';
import { roleAssignmentsErrorMessages, type RoleAssignmentsState } from './roleAssignmentsState.ts';
import { createAuditEventsPageCoordinator, type AuditEventsPageCoordinator } from './auditEventsPageCoordinator.ts';
import { auditEventsErrorMessages, type AuditEventsState } from './auditEventsState.ts';
import styles from './AdminPage.module.css';

export function AdminPage() {
  const [state, setState] = useState<UsersState>({ status: 'loading' });
  const [profilesState, setProfilesState] = useState<ProfilesState>({ status: 'loading' });
  const [roleAssignmentsState, setRoleAssignmentsState] = useState<RoleAssignmentsState>({ status: 'loading' });
  const [auditEventsState, setAuditEventsState] = useState<AuditEventsState>({ status: 'loading' });
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
  const roleAssignmentsCoordinator = useRef<RoleAssignmentsPageCoordinator | null>(null);
  if (roleAssignmentsCoordinator.current === null) {
    roleAssignmentsCoordinator.current = createRoleAssignmentsPageCoordinator({ applyState: setRoleAssignmentsState, navigateToLogin: () => window.location.assign('/login') });
  }
  const auditEventsCoordinator = useRef<AuditEventsPageCoordinator | null>(null);
  if (auditEventsCoordinator.current === null) {
    auditEventsCoordinator.current = createAuditEventsPageCoordinator({ applyState: setAuditEventsState, navigateToLogin: () => window.location.assign('/login') });
  }
  const load = useCallback(async () => { await coordinator.current?.load(); }, []);
  const loadProfiles = useCallback(async () => { await profilesCoordinator.current?.load(); }, []);
  const loadRoleAssignments = useCallback(async () => { await roleAssignmentsCoordinator.current?.load(); }, []);
  const loadAuditEvents = useCallback(async () => { await auditEventsCoordinator.current?.load(); }, []);
  useEffect(() => {
    void load();
    void loadProfiles();
    void loadRoleAssignments();
    void loadAuditEvents();
    return () => { coordinator.current?.invalidate(); profilesCoordinator.current?.invalidate(); roleAssignmentsCoordinator.current?.invalidate(); auditEventsCoordinator.current?.invalidate(); };
  }, [load, loadProfiles, loadRoleAssignments, loadAuditEvents]);

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
      <section className={styles.section} aria-labelledby="role-assignments-heading">
        <h2 id="role-assignments-heading">Role assignments</h2>
        {roleAssignmentsState.status === 'loading' && <div className={styles.status} role="status" aria-live="polite"><Loader /><span>Loading role assignments...</span></div>}
        {roleAssignmentsState.status === 'error' && <div className={styles.errorPanel} role="alert"><p>{roleAssignmentsErrorMessages[roleAssignmentsState.failure]}</p><Button type="button" onClick={() => void loadRoleAssignments()}>Retry role assignments</Button></div>}
        {roleAssignmentsState.status === 'success' && roleAssignmentsState.roleAssignments.length === 0 && <EmptyState title="No role assignments found" />}
        {roleAssignmentsState.status === 'success' && roleAssignmentsState.roleAssignments.length > 0 && <div className={styles.tableWrap}><table className={styles.table}><thead><tr><th>ID</th><th>User ID</th><th>Role</th><th>Scope type</th><th>Scope ID</th><th>Status</th><th>Assigned by</th><th>Assigned</th><th>Revoked</th></tr></thead><tbody>{roleAssignmentsState.roleAssignments.map((assignment) => <tr key={assignment.id}><td>{assignment.id}</td><td>{assignment.user_id}</td><td>{assignment.role_code}</td><td>{assignment.scope_type ?? '—'}</td><td>{assignment.scope_id ?? '—'}</td><td>{assignment.is_active ? 'Active' : 'Inactive'}</td><td>{assignment.assigned_by_user_id ?? '—'}</td><td>{assignment.assigned_at}</td><td>{assignment.revoked_at ?? '—'}</td></tr>)}</tbody></table></div>}
      </section>
      <section className={styles.section} aria-labelledby="audit-events-heading">
        <h2 id="audit-events-heading">Audit events</h2>
        {auditEventsState.status === 'loading' && <div className={styles.status} role="status" aria-live="polite"><Loader /><span>Loading audit events...</span></div>}
        {auditEventsState.status === 'error' && <div className={styles.errorPanel} role="alert"><p>{auditEventsErrorMessages[auditEventsState.failure]}</p><Button type="button" onClick={() => void loadAuditEvents()}>Retry audit events</Button></div>}
        {auditEventsState.status === 'success' && auditEventsState.auditEvents.length === 0 && <EmptyState title="No audit events found" />}
        {auditEventsState.status === 'success' && auditEventsState.auditEvents.length > 0 && <div className={styles.tableWrap}><table className={styles.table}><thead><tr><th>ID</th><th>Actor user ID</th><th>Target user ID</th><th>Event type</th><th>Summary</th><th>Details</th><th>Created</th></tr></thead><tbody>{auditEventsState.auditEvents.map((event) => <tr key={event.id}><td>{event.id}</td><td>{event.actor_user_id ?? '—'}</td><td>{event.target_user_id ?? '—'}</td><td>{event.event_type}</td><td>{event.summary ?? '—'}</td><td>{event.details === null ? '—' : JSON.stringify(event.details)}</td><td>{event.created_at}</td></tr>)}</tbody></table></div>}
      </section>
    </div>
  );
}
