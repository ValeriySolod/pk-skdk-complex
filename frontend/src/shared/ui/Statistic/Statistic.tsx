import type { HTMLAttributes, ReactNode } from 'react';
import clsx from 'clsx';

import styles from './Statistic.module.css';

export type StatisticSize = 'sm' | 'md' | 'lg';
export type StatisticTone =
  | 'neutral'
  | 'success'
  | 'warning'
  | 'danger'
  | 'info';
export type StatisticAlignment = 'start' | 'center' | 'end';
export type StatisticTrendDirection = 'up' | 'down' | 'flat';

export interface StatisticProps
  extends Omit<HTMLAttributes<HTMLDListElement>, 'prefix'> {
  label: ReactNode;
  value: ReactNode;
  prefix?: ReactNode;
  suffix?: ReactNode;
  description?: ReactNode;
  trend?: ReactNode;
  trendTone?: StatisticTone;
  trendDirection?: StatisticTrendDirection;
  size?: StatisticSize;
  align?: StatisticAlignment;
}

const trendDirectionLabel: Record<StatisticTrendDirection, string> = {
  up: 'Increase',
  down: 'Decrease',
  flat: 'No change',
};

export function Statistic({
  label,
  value,
  prefix,
  suffix,
  description,
  trend,
  trendTone = 'neutral',
  trendDirection = 'flat',
  size = 'md',
  align = 'start',
  className,
  ...props
}: StatisticProps) {
  const hasAffix = Boolean(prefix || suffix);

  return (
    <dl
      className={clsx(
        styles.statistic,
        styles[size],
        styles[`align-${align}`],
        className,
      )}
      {...props}
    >
      <dt className={styles.label}>{label}</dt>
      <dd className={styles.body}>
        <div className={clsx(styles.value, hasAffix && styles.withAffix)}>
          {prefix && <span className={styles.affix}>{prefix}</span>}
          <span className={styles.valueText}>{value}</span>
          {suffix && <span className={styles.affix}>{suffix}</span>}
        </div>

        {(trend || description) && (
          <div className={styles.meta}>
            {trend && (
              <span
                className={clsx(
                  styles.trend,
                  styles[trendTone],
                  styles[`trend-${trendDirection}`],
                )}
              >
                <span className={styles.visuallyHidden}>
                  {trendDirectionLabel[trendDirection]}:
                </span>
                <span aria-hidden="true" className={styles.trendMarker} />
                <span>{trend}</span>
              </span>
            )}

            {description && (
              <span className={styles.description}>{description}</span>
            )}
          </div>
        )}
      </dd>
    </dl>
  );
}
