import { useEffect, type ReactNode } from 'react';
import { createPortal } from 'react-dom';
import clsx from 'clsx';
import styles from './Toast.module.css';

export type ToastVariant = 'info' | 'success' | 'warning' | 'error';
export type ToastPosition = 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center';

export interface ToastProps {
  open?: boolean;
  title?: ReactNode;
  children?: ReactNode;
  variant?: ToastVariant;
  className?: string;
  closeLabel?: string;
  showCloseButton?: boolean;
  autoCloseMs?: number;
  onClose?: () => void;
  action?: ReactNode;
}

export interface ToastViewportProps {
  children: ReactNode;
  position?: ToastPosition;
  className?: string;
  portal?: boolean;
}

const toastRoleByVariant: Record<ToastVariant, 'status' | 'alert'> = {
  info: 'status',
  success: 'status',
  warning: 'alert',
  error: 'alert',
};

export function Toast({
  open = true,
  title,
  children,
  variant = 'info',
  className,
  closeLabel = 'Закрити повідомлення',
  showCloseButton = true,
  autoCloseMs,
  onClose,
  action,
}: ToastProps) {
  useEffect(() => {
    if (!open || !autoCloseMs || !onClose) {
      return undefined;
    }

    const timerId = window.setTimeout(onClose, autoCloseMs);

    return () => {
      window.clearTimeout(timerId);
    };
  }, [autoCloseMs, onClose, open]);

  if (!open) {
    return null;
  }

  const role = toastRoleByVariant[variant];

  return (
    <div
      className={clsx(styles.toast, styles[variant], className)}
      role={role}
      aria-live={role === 'alert' ? 'assertive' : 'polite'}
    >
      <div className={styles.indicator} aria-hidden="true" />

      <div className={styles.content}>
        {title && <p className={styles.title}>{title}</p>}
        {children && <div className={styles.message}>{children}</div>}
      </div>

      {action && <div className={styles.action}>{action}</div>}

      {showCloseButton && onClose && (
        <button className={styles.closeButton} type="button" aria-label={closeLabel} onClick={onClose}>
          ×
        </button>
      )}
    </div>
  );
}

export function ToastViewport({ children, position = 'top-right', className, portal = true }: ToastViewportProps) {
  const viewport = (
    <div className={clsx(styles.viewport, styles[position], className)} role="region" aria-label="Повідомлення">
      {children}
    </div>
  );

  if (!portal) {
    return viewport;
  }

  return createPortal(viewport, document.body);
}
