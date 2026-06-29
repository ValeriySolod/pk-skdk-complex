import type { CSSProperties, ReactNode } from 'react';
import clsx from 'clsx';

import styles from './Flex.module.css';

export type FlexDirection = 'row' | 'column' | 'row-reverse' | 'column-reverse';

export type FlexAlign = 'start' | 'center' | 'end' | 'stretch' | 'baseline';

export type FlexJustify =
  | 'start'
  | 'center'
  | 'end'
  | 'between'
  | 'around'
  | 'evenly';

export type FlexGap = 'none' | 'xs' | 'sm' | 'md' | 'lg' | 'xl';

export interface FlexProps {
  children: ReactNode;
  direction?: FlexDirection;
  align?: FlexAlign;
  justify?: FlexJustify;
  gap?: FlexGap;
  wrap?: boolean;
  className?: string;
  style?: CSSProperties;
}

const directionClassNames: Record<FlexDirection, string> = {
  row: styles.row,
  column: styles.column,
  'row-reverse': styles.rowReverse,
  'column-reverse': styles.columnReverse,
};

const alignClassNames: Record<FlexAlign, string> = {
  start: styles.alignStart,
  center: styles.alignCenter,
  end: styles.alignEnd,
  stretch: styles.alignStretch,
  baseline: styles.alignBaseline,
};

const justifyClassNames: Record<FlexJustify, string> = {
  start: styles.justifyStart,
  center: styles.justifyCenter,
  end: styles.justifyEnd,
  between: styles.justifyBetween,
  around: styles.justifyAround,
  evenly: styles.justifyEvenly,
};

export function Flex({
  children,
  direction = 'row',
  align = 'stretch',
  justify = 'start',
  gap = 'none',
  wrap = false,
  className,
  style,
}: FlexProps) {
  return (
    <div
      className={clsx(
        styles.flex,
        directionClassNames[direction],
        alignClassNames[align],
        justifyClassNames[justify],
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
