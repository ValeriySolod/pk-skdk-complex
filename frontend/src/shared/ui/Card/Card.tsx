import type { HTMLAttributes, ReactNode } from 'react';
import styles from './Card.module.css';

type CardVariant = 'default' | 'outlined' | 'elevated';
type CardPadding = 'none' | 'sm' | 'md' | 'lg';

export type CardProps = HTMLAttributes<HTMLDivElement> & {
  children: ReactNode;
  title?: ReactNode;
  description?: ReactNode;
  actions?: ReactNode;
  variant?: CardVariant;
  padding?: CardPadding;
};

export function Card({
  children,
  title,
  description,
  actions,
  variant = 'default',
  padding = 'md',
  className = '',
  ...props
}: CardProps) {
  const hasHeader = Boolean(title || description || actions);
  const classNames = [styles.card, styles[variant], styles[`padding-${padding}`], className]
    .filter(Boolean)
    .join(' ');

  return (
    <div className={classNames} {...props}>
      {hasHeader && (
        <div className={styles.header}>
          {(title || description) && (
            <div className={styles.heading}>
              {title && <div className={styles.title}>{title}</div>}
              {description && <div className={styles.description}>{description}</div>}
            </div>
          )}
          {actions && <div className={styles.actions}>{actions}</div>}
        </div>
      )}
      <div className={styles.body}>{children}</div>
    </div>
  );
}
