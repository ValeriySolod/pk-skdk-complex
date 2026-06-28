import type React from 'react';
import styles from './Switch.module.css';

export interface SwitchProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: React.ReactNode;
  helperText?: React.ReactNode;
  error?: React.ReactNode;
}

export function Switch({
  id,
  label,
  helperText,
  error,
  className = '',
  disabled,
  required,
  'aria-describedby': ariaDescribedBy,
  ...props
}: SwitchProps) {
  const switchId = id ?? props.name;
  const helperTextId = helperText && switchId ? `${switchId}-helper` : undefined;
  const errorId = error && switchId ? `${switchId}-error` : undefined;

  const describedBy = [ariaDescribedBy, errorId, !error ? helperTextId : undefined]
    .filter(Boolean)
    .join(' ') || undefined;

  return (
    <div className={`${styles.container} ${disabled ? styles.disabled : ''}`}>
      <div className={styles.controlRow}>
        <input
          id={switchId}
          className={`${styles.switch} ${error ? styles.errorState : ''} ${className}`}
          type="checkbox"
          role="switch"
          disabled={disabled}
          required={required}
          aria-invalid={error ? 'true' : undefined}
          aria-describedby={describedBy}
          {...props}
        />

        {label && (
          <label className={styles.label} htmlFor={switchId}>
            {label}
            {required && <span className={styles.required}> *</span>}
          </label>
        )}
      </div>

      {error && (
        <p className={styles.error} id={errorId}>
          {error}
        </p>
      )}

      {!error && helperText && (
        <p className={styles.helper} id={helperTextId}>
          {helperText}
        </p>
      )}
    </div>
  );
}
