import type { CSSProperties } from 'react';

import styles from './Skeleton.module.css';

export type SkeletonVariant = 'text' | 'rectangular' | 'rounded' | 'circle';

export interface SkeletonProps {
  variant?: SkeletonVariant;
  width?: string | number;
  height?: string | number;
  lines?: number;
  animated?: boolean;
  className?: string;
  'aria-label'?: string;
}

const DEFAULT_TEXT_HEIGHT = '1em';
const DEFAULT_LINE_GAP = 8;

function toCssSize(value: string | number | undefined): string | undefined {
  if (typeof value === 'number') {
    return `${value}px`;
  }

  return value;
}

function getLineCount(lines: number | undefined): number {
  if (typeof lines !== 'number' || !Number.isFinite(lines)) {
    return 1;
  }

  return Math.max(1, Math.floor(lines));
}

function buildClassName(...classes: Array<string | undefined>): string {
  return classes.filter(Boolean).join(' ');
}

export function Skeleton({
  variant = 'text',
  width,
  height,
  lines = 1,
  animated = true,
  className,
  'aria-label': ariaLabel,
}: SkeletonProps) {
  const lineCount = getLineCount(lines);
  const skeletonClassName = buildClassName(
    styles.skeleton,
    styles[variant],
    animated ? styles.animated : undefined,
    lineCount === 1 ? className : undefined,
  );
  const skeletonStyle: CSSProperties = {
    width: toCssSize(width),
    height: toCssSize(height ?? (variant === 'text' ? DEFAULT_TEXT_HEIGHT : undefined)),
  };

  if (lineCount > 1) {
    const groupStyle: CSSProperties = {
      width: toCssSize(width),
      gap: DEFAULT_LINE_GAP,
    };

    return (
      <span
        className={buildClassName(styles.group, className)}
        style={groupStyle}
        role={ariaLabel ? 'status' : undefined}
        aria-label={ariaLabel}
        aria-hidden={ariaLabel ? undefined : true}
      >
        {Array.from({ length: lineCount }, (_, index) => (
          <span
            key={index}
            className={skeletonClassName}
            style={{
              ...skeletonStyle,
              width: variant === 'text' && index === lineCount - 1 ? '80%' : skeletonStyle.width,
            }}
          />
        ))}
      </span>
    );
  }

  return (
    <span
      className={skeletonClassName}
      style={skeletonStyle}
      role={ariaLabel ? 'status' : undefined}
      aria-label={ariaLabel}
      aria-hidden={ariaLabel ? undefined : true}
    />
  );
}
