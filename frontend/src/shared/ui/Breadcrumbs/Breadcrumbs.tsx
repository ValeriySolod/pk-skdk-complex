import type { ReactNode } from 'react';
import clsx from 'clsx';
import styles from './Breadcrumbs.module.css';

export interface BreadcrumbItem {
  label: string;
  href?: string;
  current?: boolean;
}

export interface BreadcrumbsProps {
  items: BreadcrumbItem[];
  separator?: ReactNode;
  className?: string;
}

export function Breadcrumbs({
  items,
  separator = '/',
  className,
}: BreadcrumbsProps) {
  if (items.length === 0) {
    return null;
  }

  return (
    <nav className={clsx(styles.breadcrumbs, className)} aria-label="Breadcrumb">
      <ol className={styles.list}>
        {items.map((item, index) => {
          const isLast = index === items.length - 1;
          const isCurrent = item.current || isLast;
          const key = `${item.label}-${item.href ?? index}`;

          return (
            <li className={styles.item} key={key}>
              {item.href && !isCurrent ? (
                <a className={styles.link} href={item.href}>
                  {item.label}
                </a>
              ) : (
                <span className={styles.current} aria-current="page">
                  {item.label}
                </span>
              )}

              {!isLast && (
                <span className={styles.separator} aria-hidden="true">
                  {separator}
                </span>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
