import { NavLink, Outlet } from 'react-router-dom';

import type { User } from '../api/auth';
import { AppShell } from '../shared/ui';
import { modules } from './moduleRegistry';
import styles from './ApplicationShell.module.css';

export type ApplicationShellProps = {
  user: User;
  onLogout: () => void;
};

export function ApplicationShell({ user, onLogout }: ApplicationShellProps) {
  const displayName = user.full_name || user.username;

  const header = (
    <div className={styles.header}>
      <div className={styles.brand}>
        <p className={styles.title}>PK SKDK</p>
        <p className={styles.subtitle}>Correspondence delivery control</p>
      </div>

      <div className={styles.userPanel}>
        <div className={styles.userText}>
          <span className={styles.userName}>{displayName}</span>
          <span className={styles.userRole}>{user.role}</span>
        </div>
        <button className={styles.logoutButton} type="button" onClick={onLogout}>
          Logout
        </button>
      </div>
    </div>
  );

  const sidebar = (
    <div className={styles.sidebar}>
      <h1 className={styles.sidebarTitle}>PK SKDK</h1>
      <p className={styles.sidebarSubtitle}>Application modules</p>
      <nav className={styles.nav} aria-label="Application modules">
        <NavLink
          className={({ isActive }) =>
            isActive ? `${styles.navLink} ${styles.activeNavLink}` : styles.navLink
          }
          to="/"
          end
        >
          Home
        </NavLink>
        {modules.map((module) => (
          <NavLink
            className={({ isActive }) =>
              isActive ? `${styles.navLink} ${styles.activeNavLink}` : styles.navLink
            }
            key={module.code}
            to={module.path}
          >
            {module.title}
          </NavLink>
        ))}
      </nav>
    </div>
  );

  return (
    <AppShell
      className={styles.shell}
      fullHeight
      header={header}
      sidebar={sidebar}
      sidebarWidth="280px"
    >
      <div className={styles.content}>
        <Outlet />
      </div>
    </AppShell>
  );
}
