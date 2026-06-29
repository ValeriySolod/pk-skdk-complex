import type { ReactNode } from 'react';
import clsx from 'clsx';
import styles from './Divider.module.css';

export type DividerOrientation = 'horizontal' | 'vertical';
export type DividerVariant = 'solid' | 'dashed' | 'dotted';

export interface DividerProps {
  orientation?: DividerOrientation;
  variant?: DividerVariant;
  label?: ReactNode;
  className?: string;
}

function hasRenderableLabel(label: ReactNode) {
  return label !== undefined && label !== null && label !== false && label !== '';
}

export function Divider({
  orientation = 'horizontal',
  variant = 'solid',
  label,
  className,
}: DividerProps) {
  const shouldRenderLabel =
    orientation === 'horizontal' && hasRenderableLabel(label);

  return (
    <div
      className={clsx(
        styles.divider,
        styles[orientation],
        styles[variant],
        shouldRenderLabel && styles.withLabel,
        className,
      )}
      role="separator"
      aria-orientation={orientation}
    >
      {shouldRenderLabel && (
        <>
          <span className={styles.line} aria-hidden="true" />
          <span className={styles.label}>{label}</span>
          <span className={styles.line} aria-hidden="true" />
        </>
      )}
    </div>
  );
}
