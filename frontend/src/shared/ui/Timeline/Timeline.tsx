import type React from 'react';
import clsx from 'clsx';

import styles from './Timeline.module.css';

export type TimelineItemStatus = 'default' | 'success' | 'warning' | 'danger';

export interface TimelineItem {
  id: string;
  title: React.ReactNode;
  description?: React.ReactNode;
  meta?: React.ReactNode;
  status?: TimelineItemStatus;
}

export interface TimelineProps {
  items: TimelineItem[];
  className?: string;
}

export function Timeline({ items, className }: TimelineProps) {
  if (items.length === 0) {
    return null;
  }

  return (
    <ol className={clsx(styles.timeline, className)}>
      {items.map((item) => {
        const status = item.status ?? 'default';

        return (
          <li key={item.id} className={clsx(styles.item, styles[status])}>
            <span className={styles.markerWrap} aria-hidden="true">
              <span className={styles.marker} />
            </span>

            <div className={styles.content}>
              <div className={styles.header}>
                <div className={styles.title}>{item.title}</div>
                {item.meta && <div className={styles.meta}>{item.meta}</div>}
              </div>

              {item.description && (
                <div className={styles.description}>{item.description}</div>
              )}
            </div>
          </li>
        );
      })}
    </ol>
  );
}
