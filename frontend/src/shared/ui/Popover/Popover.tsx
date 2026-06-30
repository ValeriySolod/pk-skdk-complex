import { useCallback, useEffect, useId, useRef, type ReactNode } from 'react';
import clsx from 'clsx';
import styles from './Popover.module.css';

export type PopoverPlacement =
  | 'top'
  | 'bottom'
  | 'left'
  | 'right';

export interface PopoverProps {
  open: boolean;
  anchor: ReactNode;
  children: ReactNode;
  onOpenChange?: (open: boolean) => void;
  placement?: PopoverPlacement;
  closeOnOutsideClick?: boolean;
  closeOnEscape?: boolean;
  disabled?: boolean;
  className?: string;
}

export function Popover({
  open,
  anchor,
  children,
  onOpenChange,
  placement = 'bottom',
  closeOnOutsideClick = true,
  closeOnEscape = true,
  disabled = false,
  className,
}: PopoverProps) {
  const popoverId = useId();
  const wrapperRef = useRef<HTMLDivElement>(null);

  const requestOpenChange = useCallback((nextOpen: boolean) => {
    if (nextOpen !== open) {
      onOpenChange?.(nextOpen);
    }
  }, [onOpenChange, open]);

  useEffect(() => {
    if (!open || !closeOnOutsideClick) {
      return undefined;
    }

    function handlePointerDown(event: PointerEvent) {
      if (!wrapperRef.current?.contains(event.target as Node)) {
        requestOpenChange(false);
      }
    }

    document.addEventListener('pointerdown', handlePointerDown);

    return () => {
      document.removeEventListener('pointerdown', handlePointerDown);
    };
  }, [closeOnOutsideClick, open, requestOpenChange]);

  useEffect(() => {
    if (!open || !closeOnEscape) {
      return undefined;
    }

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        requestOpenChange(false);
      }
    }

    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [closeOnEscape, open, requestOpenChange]);

  return (
    <div ref={wrapperRef} className={clsx(styles.wrapper, className)}>
      <button
        type="button"
        className={styles.trigger}
        aria-haspopup="dialog"
        aria-expanded={open}
        aria-controls={open ? popoverId : undefined}
        disabled={disabled}
        onClick={() => requestOpenChange(!open)}
      >
        {anchor}
      </button>

      {open && (
        <div id={popoverId} role="dialog" className={clsx(styles.popover, styles[placement])}>
          {children}
        </div>
      )}
    </div>
  );
}
