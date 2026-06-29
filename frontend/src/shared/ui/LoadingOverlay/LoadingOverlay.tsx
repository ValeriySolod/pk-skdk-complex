import clsx from 'clsx';
import styles from './LoadingOverlay.module.css';

export interface LoadingOverlayProps {
  visible?: boolean;
  label?: string;
  fullScreen?: boolean;
  backdrop?: boolean;
  className?: string;
}

export function LoadingOverlay({
  visible = true,
  label = 'Завантаження...',
  fullScreen = false,
  backdrop = true,
  className,
}: LoadingOverlayProps) {
  if (!visible) {
    return null;
  }

  return (
    <div
      className={clsx(
        styles.overlay,
        fullScreen ? styles.fullScreen : styles.contained,
        backdrop && styles.backdrop,
        className,
      )}
      role="status"
      aria-live="polite"
      aria-busy="true"
    >
      <span className={styles.spinner} aria-hidden="true" />
      <span className={styles.label}>{label}</span>
    </div>
  );
}
