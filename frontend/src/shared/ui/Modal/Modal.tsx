import { useEffect, useId, type MouseEvent, type ReactNode } from 'react';
import { createPortal } from 'react-dom';
import clsx from 'clsx';
import styles from './Modal.module.css';

export interface ModalProps {
  open: boolean;
  title?: ReactNode;
  description?: ReactNode;
  children: ReactNode;
  footer?: ReactNode;
  className?: string;
  contentClassName?: string;
  overlayClassName?: string;
  closeLabel?: string;
  closeOnOverlayClick?: boolean;
  closeOnEscape?: boolean;
  showCloseButton?: boolean;
  labelledBy?: string;
  describedBy?: string;
  onClose: () => void;
}

export function Modal({
  open,
  title,
  description,
  children,
  footer,
  className,
  contentClassName,
  overlayClassName,
  closeLabel = 'Закрити модальне вікно',
  closeOnOverlayClick = true,
  closeOnEscape = true,
  showCloseButton = true,
  labelledBy,
  describedBy,
  onClose,
}: ModalProps) {
  const generatedId = useId();
  const titleId = labelledBy ?? (title ? `${generatedId}-title` : undefined);
  const descriptionId = describedBy ?? (description ? `${generatedId}-description` : undefined);

  useEffect(() => {
    if (!open || !closeOnEscape) {
      return undefined;
    }

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [closeOnEscape, onClose, open]);

  useEffect(() => {
    if (!open) {
      return undefined;
    }

    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    return () => {
      document.body.style.overflow = originalOverflow;
    };
  }, [open]);

  if (!open) {
    return null;
  }

  const handleOverlayMouseDown = (event: MouseEvent<HTMLDivElement>) => {
    if (closeOnOverlayClick && event.target === event.currentTarget) {
      onClose();
    }
  };

  return createPortal(
    <div
      className={clsx(styles.overlay, overlayClassName)}
      onMouseDown={handleOverlayMouseDown}
      role="presentation"
    >
      <section
        className={clsx(styles.modal, className)}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        aria-describedby={descriptionId}
      >
        {(title || showCloseButton) && (
          <header className={styles.header}>
            <div className={styles.heading}>
              {title && (
                <h2 className={styles.title} id={titleId}>
                  {title}
                </h2>
              )}

              {description && (
                <p className={styles.description} id={descriptionId}>
                  {description}
                </p>
              )}
            </div>

            {showCloseButton && (
              <button className={styles.closeButton} type="button" aria-label={closeLabel} onClick={onClose}>
                ×
              </button>
            )}
          </header>
        )}

        <div className={clsx(styles.content, contentClassName)}>{children}</div>

        {footer && <footer className={styles.footer}>{footer}</footer>}
      </section>
    </div>,
    document.body,
  );
}
