import type { ReactNode } from 'react';
import clsx from 'clsx';

import styles from './Notification.module.css';

export type NotificationVariant = 'info' | 'success' | 'warning' | 'danger';

export interface NotificationProps {
  title?: string;
  message?: string;
  variant?: NotificationVariant;
  icon?: ReactNode;
  action?: ReactNode;
  onClose?: () => void;
  className?: string;
}

const notificationRoleByVariant: Record<NotificationVariant, 'alert' | 'status'> = {
  info: 'status',
  success: 'status',
  warning: 'alert',
  danger: 'alert',
};

export function Notification({
  title,
  message,
  variant = 'info',
  icon,
  action,
  onClose,
  className,
}: NotificationProps) {
  if (!title && !message) {
    return null;
  }

  const role = notificationRoleByVariant[variant];

  return (
    <section
      className={clsx(styles.notification, styles[variant], className)}
      role={role}
      aria-live={role === 'alert' ? 'assertive' : 'polite'}
    >
      {icon && (
        <div className={styles.icon} aria-hidden="true">
          {icon}
        </div>
      )}

      <div className={styles.content}>
        {title && <p className={styles.title}>{title}</p>}
        {message && <p className={styles.message}>{message}</p>}
      </div>

      {action && <div className={styles.action}>{action}</div>}

      {onClose && (
        <button
          className={styles.closeButton}
          type="button"
          aria-label="Close notification"
          onClick={onClose}
        >
          <span aria-hidden="true">×</span>
        </button>
      )}
    </section>
  );
}
