import clsx from 'clsx';
import styles from './ProgressBar.module.css';

export type ProgressBarVariant = 'default' | 'success' | 'warning' | 'danger';

export interface ProgressBarProps {
  value: number;
  max?: number;
  label?: string;
  showValue?: boolean;
  variant?: ProgressBarVariant;
  className?: string;
}

function getSafeMax(max: number | undefined) {
  if (max === undefined || max <= 0) {
    return 100;
  }

  return max;
}

function clampValue(value: number, max: number) {
  return Math.min(Math.max(value, 0), max);
}

export function ProgressBar({
  value,
  max,
  label,
  showValue = false,
  variant = 'default',
  className,
}: ProgressBarProps) {
  const safeMax = getSafeMax(max);
  const clampedValue = clampValue(value, safeMax);
  const percentage = Math.round((clampedValue / safeMax) * 100);

  return (
    <div className={clsx(styles.progressBar, className)}>
      {(label || showValue) && (
        <div className={styles.header}>
          {label && <span className={styles.label}>{label}</span>}
          {showValue && <span className={styles.value}>{percentage}%</span>}
        </div>
      )}

      <div
        className={styles.track}
        role="progressbar"
        aria-valuemin={0}
        aria-valuemax={safeMax}
        aria-valuenow={clampedValue}
      >
        <div
          className={clsx(styles.fill, styles[variant])}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
