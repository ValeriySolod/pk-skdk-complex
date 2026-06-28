import { useId, type ReactElement, type ReactNode } from 'react';
import clsx from 'clsx';
import styles from './Tooltip.module.css';

export type TooltipPlacement = 'top' | 'right' | 'bottom' | 'left';

export interface TooltipProps {
  children: ReactElement;
  content: ReactNode;
  placement?: TooltipPlacement;
  disabled?: boolean;
  className?: string;
  tooltipClassName?: string;
}

export function Tooltip({
  children,
  content,
  placement = 'top',
  disabled = false,
  className,
  tooltipClassName,
}: TooltipProps) {
  const tooltipId = useId();

  if (disabled || !content) {
    return children;
  }

  return (
    <span className={clsx(styles.wrapper, className)}>
      <span aria-describedby={tooltipId} className={styles.trigger}>
        {children}
      </span>

      <span
        id={tooltipId}
        role="tooltip"
        className={clsx(styles.tooltip, styles[placement], tooltipClassName)}
      >
        {content}
      </span>
    </span>
  );
}