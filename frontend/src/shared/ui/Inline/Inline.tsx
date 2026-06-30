import type { CSSProperties, ReactNode } from 'react';
import clsx from 'clsx';

import styles from './Inline.module.css';

export type InlineAlign = 'start' | 'center' | 'end' | 'stretch' | 'baseline';

export type InlineGap = 'none' | 'xs' | 'sm' | 'md' | 'lg' | 'xl';

export interface InlineProps {
  children: ReactNode;
  gap?: InlineGap;
  align?: InlineAlign;
  wrap?: boolean;
  className?: string;
  style?: CSSProperties;
}

export function Inline({
  children,
  gap = 'none',
  align = 'stretch',
  wrap = false,
  className,
  style,
}: InlineProps) {
  return (
    <div
      className={clsx(
        styles.inline,
        styles[align],
        styles[gap],
        wrap && styles.wrap,
        className,
      )}
      style={style}
    >
      {children}
    </div>
  );
}
