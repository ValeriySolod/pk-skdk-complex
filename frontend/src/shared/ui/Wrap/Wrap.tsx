import type { CSSProperties, ReactNode } from 'react';
import clsx from 'clsx';

import styles from './Wrap.module.css';

export type WrapGap = 'none' | 'xs' | 'sm' | 'md' | 'lg' | 'xl';

export type WrapAlign = 'start' | 'center' | 'end' | 'stretch';

export interface WrapProps {
  children: ReactNode;
  gap?: WrapGap;
  align?: WrapAlign;
  className?: string;
  style?: CSSProperties;
}

export function Wrap({
  children,
  gap = 'md',
  align = 'start',
  className,
  style,
}: WrapProps) {
  return (
    <div
      className={clsx(styles.wrap, styles[gap], styles[align], className)}
      style={style}
    >
      {children}
    </div>
  );
}
