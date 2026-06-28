import type React from 'react';
import styles from './Checkbox.module.css';

export interface CheckboxProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: React.ReactNode;
  helperText?: React.ReactNode;
  error?: React.ReactNode;
}

export function Checkbox({
  id,
  label,
  helperText,
  error,
  className = '',
  disabled,
  required,
  'aria-describedby': ariaDescribedBy,
  ...props
}: CheckboxProps) {
  const checkboxId = id ?? props.name;
  const helperTextId = helperText && checkboxId ? `${checkboxId}-helper` : undefined;
  const errorId = error && checkboxId ? `${checkboxId}-error` : undefined;

  const describedBy = [ariaDescribedBy, errorId, !error ? helperTextId : undefined]
    .filter(Boolean)
    .join(' ') || undefined;

  return (
    <div className={`${styles.container} ${disabled ? styles.disabled : ''}`}>
      <div className={styles.controlRow}>
        <input
          id={checkboxId}
          className={`${styles.checkbox} ${error ? styles.errorState : ''} ${className}`}
          type="checkbox"
          disabled={disabled}
          required={required}
          aria-invalid={error ? 'true' : undefined}
          aria-describedby={describedBy}
          {...props}
        />

        {label && (
          <label className={styles.label} htmlFor={checkboxId}>
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
