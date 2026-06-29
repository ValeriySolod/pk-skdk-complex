import type { ReactNode } from 'react';
import clsx from 'clsx';

import styles from './Banner.module.css';

export type BannerVariant = 'info' | 'success' | 'warning' | 'danger';

export interface BannerProps {
  title?: string;
  children?: ReactNode;
  variant?: BannerVariant;
  icon?: ReactNode;
  action?: ReactNode;
  dismissible?: boolean;
  onDismiss?: () => void;
  className?: string;
}

const bannerRoleByVariant: Record<BannerVariant, 'alert' | 'status'> = {
  info: 'status',
  success: 'status',
  warning: 'alert',
  danger: 'alert',
};

export function Banner({
  title,
  children,
  variant = 'info',
  icon,
  action,
  dismissible = false,
  onDismiss,
  className,
}: BannerProps) {
  if (!title && !children) {
    return null;
  }

  const hasControls = Boolean(action || dismissible);

  return (
    <section
      className={clsx(styles.banner, styles[variant], className)}
      role={bannerRoleByVariant[variant]}
    >
      <div className={styles.body}>
        {icon && <div className={styles.icon}>{icon}</div>}

        <div className={styles.content}>
          {title && <div className={styles.title}>{title}</div>}
          {children && <div className={styles.message}>{children}</div>}
        </div>
      </div>

      {hasControls && (
        <div className={styles.controls}>
          {action && <div className={styles.action}>{action}</div>}
          {dismissible && (
            <button
              aria-label="Dismiss banner"
              className={styles.dismissButton}
              onClick={onDismiss}
              type="button"
            >
              <span aria-hidden="true">×</span>
            </button>
          )}
        </div>
      )}
    </section>
  );
}
