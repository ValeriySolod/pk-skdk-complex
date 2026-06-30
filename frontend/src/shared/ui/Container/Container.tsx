import type { ReactNode } from 'react';
import clsx from 'clsx';

import styles from './Container.module.css';

export type ContainerSize = 'sm' | 'md' | 'lg' | 'xl' | 'full';

export interface ContainerProps {
  children: ReactNode;
  size?: ContainerSize;
  className?: string;
}

export function Container({
  children,
  size = 'lg',
  className,
}: ContainerProps) {
  return (
    <div className={clsx(styles.container, styles[size], className)}>
      {children}
    </div>
  );
}
