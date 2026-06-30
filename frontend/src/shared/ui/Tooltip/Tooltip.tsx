import {
  cloneElement,
  useId,
  useState,
  type FocusEvent,
  type KeyboardEvent,
  type MouseEvent,
  type ReactElement,
  type ReactNode,
} from 'react';
import clsx from 'clsx';
import styles from './Tooltip.module.css';

export type TooltipPlacement =
  | 'top'
  | 'bottom'
  | 'left'
  | 'right';

export interface TooltipProps {
  content: ReactNode;
  children: ReactElement<TooltipTriggerProps>;
  placement?: TooltipPlacement;
  disabled?: boolean;
  className?: string;
}

type TooltipTriggerProps = {
  'aria-describedby'?: string;
  onMouseEnter?: (event: MouseEvent<HTMLElement>) => void;
  onMouseLeave?: (event: MouseEvent<HTMLElement>) => void;
  onFocus?: (event: FocusEvent<HTMLElement>) => void;
  onBlur?: (event: FocusEvent<HTMLElement>) => void;
  onKeyDown?: (event: KeyboardEvent<HTMLElement>) => void;
  tabIndex?: number;
};

export function Tooltip({
  content,
  children,
  placement = 'top',
  disabled = false,
  className,
}: TooltipProps) {
  const tooltipId = useId();
  const [isOpen, setIsOpen] = useState(false);

  if (disabled) {
    return children;
  }

  const trigger = children;
  const describedBy = trigger.props['aria-describedby']
    ? `${trigger.props['aria-describedby']} ${tooltipId}`
    : tooltipId;

  const handleMouseEnter = (event: MouseEvent<HTMLElement>) => {
    trigger.props.onMouseEnter?.(event);
    setIsOpen(true);
  };

  const handleMouseLeave = (event: MouseEvent<HTMLElement>) => {
    trigger.props.onMouseLeave?.(event);
    setIsOpen(false);
  };

  const handleFocus = (event: FocusEvent<HTMLElement>) => {
    trigger.props.onFocus?.(event);
    setIsOpen(true);
  };

  const handleBlur = (event: FocusEvent<HTMLElement>) => {
    trigger.props.onBlur?.(event);
    setIsOpen(false);
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLElement>) => {
    trigger.props.onKeyDown?.(event);

    if (event.key === 'Escape') {
      setIsOpen(false);
    }
  };

  return (
    <span className={clsx(styles.wrapper, className)}>
      {cloneElement(trigger, {
        'aria-describedby': describedBy,
        onMouseEnter: handleMouseEnter,
        onMouseLeave: handleMouseLeave,
        onFocus: handleFocus,
        onBlur: handleBlur,
        onKeyDown: handleKeyDown,
      })}

      {isOpen && (
        <span
          id={tooltipId}
          role="tooltip"
          className={clsx(styles.tooltip, styles[placement])}
        >
          {content}
        </span>
      )}
    </span>
  );
}
