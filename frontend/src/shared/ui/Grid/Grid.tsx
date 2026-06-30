import type { CSSProperties, ReactNode } from 'react';
import clsx from 'clsx';

import styles from './Grid.module.css';

export type GridGap = 'none' | 'xs' | 'sm' | 'md' | 'lg' | 'xl';

export interface GridProps {
  children: ReactNode;
  columns?: number;
  gap?: GridGap;
  className?: string;
}

export function Grid({
  children,
  columns = 1,
  gap = 'md',
  className,
}: GridProps) {
  const gridStyle = {
    '--grid-columns': columns,
  } as CSSProperties;

  return (
    <div className={clsx(styles.grid, styles[gap], className)} style={gridStyle}>
      {children}
    </div>
  );
}
