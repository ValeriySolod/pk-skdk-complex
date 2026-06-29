import { useId, type ReactNode } from 'react';
import clsx from 'clsx';

import styles from './EmptyState.module.css';

export interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: ReactNode;
  action?: ReactNode;
  className?: string;
}

export function EmptyState({
  title,
  description,
  icon,
  action,
  className,
}: EmptyStateProps) {
  const titleId = useId();

  return (
    <section className={clsx(styles.emptyState, className)} aria-labelledby={titleId}>
      {icon && (
        <div className={styles.icon} aria-hidden="true">
          {icon}
        </div>
      )}

      <div className={styles.content}>
        <h2 id={titleId} className={styles.title}>
          {title}
        </h2>

        {description && <p className={styles.description}>{description}</p>}
      </div>

      {action && <div className={styles.action}>{action}</div>}
    </section>
  );
}
