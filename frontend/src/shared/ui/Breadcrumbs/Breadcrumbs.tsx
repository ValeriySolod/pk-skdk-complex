import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import clsx from 'clsx';
import styles from './Breadcrumbs.module.css';

export interface BreadcrumbItem {
  label: ReactNode;
  href?: string;
  isCurrent?: boolean;
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
  return (
    <nav className={clsx(styles.breadcrumbs, className)} aria-label="Breadcrumb">
      <ol className={styles.list}>
        {items.map((item, index) => {
          const isCurrent = item.isCurrent || index === items.length - 1;
          const content = item.href && !isCurrent ? (
            <Link className={styles.link} to={item.href}>
              {item.label}
            </Link>
          ) : (
            <span className={styles.current} aria-current={isCurrent ? 'page' : undefined}>
              {item.label}
            </span>
          );

          return (
            <li className={styles.item} key={`${index}-${item.href ?? 'breadcrumb'}`}>
              {index > 0 && (
                <span className={styles.separator} aria-hidden="true">
                  {separator}
                </span>
              )}
              {content}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
