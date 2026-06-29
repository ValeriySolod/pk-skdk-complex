import type { ReactNode } from 'react';
import clsx from 'clsx';

import styles from './Alert.module.css';

export type AlertVariant = 'info' | 'success' | 'warning' | 'danger';

export interface AlertProps {
  title?: string;
  children?: ReactNode;
  variant?: AlertVariant;
  icon?: ReactNode;
  action?: ReactNode;
  className?: string;
}

const alertRoleByVariant: Record<AlertVariant, 'alert' | 'status'> = {
  info: 'status',
  success: 'status',
  warning: 'alert',
  danger: 'alert',
};

export function Alert({
  title,
  children,
  variant = 'info',
  icon,
  action,
  className,
}: AlertProps) {
  if (!title && !children) {
    return null;
  }

  return (
    <div
      className={clsx(styles.alert, styles[variant], className)}
      role={alertRoleByVariant[variant]}
    >
      {icon && <div className={styles.icon}>{icon}</div>}

      <div className={styles.content}>
        {title && <div className={styles.title}>{title}</div>}
        {children && <div className={styles.message}>{children}</div>}
      </div>

      {action && <div className={styles.action}>{action}</div>}
    </div>
  );
}
