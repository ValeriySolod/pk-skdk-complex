import type { CSSProperties, ReactNode } from 'react';
import clsx from 'clsx';

import styles from './AppShell.module.css';

export type AppShellSidebarPosition = 'left' | 'right';

export interface AppShellProps {
  header?: ReactNode;
  sidebar?: ReactNode;
  children: ReactNode;
  footer?: ReactNode;
  sidebarPosition?: AppShellSidebarPosition;
  sidebarWidth?: string;
  fullHeight?: boolean;
  className?: string;
}

type AppShellStyle = CSSProperties & {
  '--app-shell-sidebar-width'?: string;
};

export function AppShell({
  header,
  sidebar,
  children,
  footer,
  sidebarPosition = 'left',
  sidebarWidth = '280px',
  fullHeight = false,
  className,
}: AppShellProps) {
  const hasSidebar = Boolean(sidebar);

  const shellStyle: AppShellStyle = {
    '--app-shell-sidebar-width': sidebarWidth,
  };

  const sidebarElement = hasSidebar ? (
    <aside className={styles.sidebar}>{sidebar}</aside>
  ) : null;

  return (
    <div
      className={clsx(styles.shell, fullHeight && styles.fullHeight, className)}
      style={shellStyle}
    >
      {header ? <header className={styles.header}>{header}</header> : null}

      <main
        className={clsx(
          styles.main,
          hasSidebar && styles.withSidebar,
          hasSidebar && styles[sidebarPosition],
        )}
      >
        {sidebarPosition === 'left' ? sidebarElement : null}
        <div className={styles.content}>{children}</div>
        {sidebarPosition === 'right' ? sidebarElement : null}
      </main>

      {footer ? <footer className={styles.footer}>{footer}</footer> : null}
    </div>
  );
}
