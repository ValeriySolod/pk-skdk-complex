import type { HTMLAttributes, ReactNode } from 'react';
import clsx from 'clsx';
import styles from './Card.module.css';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  header?: ReactNode;
  description?: ReactNode;
  actions?: ReactNode;
  variant?: 'default' | 'outlined' | 'elevated';
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

export function Card({
  children,
  header,
  description,
  actions,
  variant = 'default',
  padding = 'md',
  className,
  ...props
}: CardProps) {
  return (
    <div
      className={clsx(
        styles.card,
        styles[variant],
        styles[`padding-${padding}`],
        className
      )}
      {...props}
    >
      {(header || description || actions) && (
        <div className={styles.header}>
          <div className={styles.headerContent}>
            {header && <div className={styles.title}>{header}</div>}
            {description && (
              <div className={styles.description}>{description}</div>
            )}
          </div>

          {actions && <div className={styles.actions}>{actions}</div>}
        </div>
      )}

      <div className={styles.body}>{children}</div>
    </div>
  );
}