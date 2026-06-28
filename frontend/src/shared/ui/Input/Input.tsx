import type { InputHTMLAttributes } from 'react';
import clsx from 'clsx';
import styles from './Input.module.css';

export type InputProps = InputHTMLAttributes<HTMLInputElement> & {
  label?: string;
  error?: string;
  helperText?: string;
};

export function Input({
  label,
  error,
  helperText,
  className,
  id,
  required,
  'aria-describedby': ariaDescribedBy,
  ...props
}: InputProps) {
  const helperId = helperText && id ? `${id}-helper` : undefined;
  const errorId = error && id ? `${id}-error` : undefined;
  const describedBy = [ariaDescribedBy, helperId, errorId].filter(Boolean).join(' ') || undefined;

  return (
    <label className={styles.wrapper}>
      {label && (
        <span className={styles.label}>
          {label}
          {required && <span aria-hidden="true"> *</span>}
        </span>
      )}

      <input
        id={id}
        className={clsx(styles.input, error && styles.inputError, className)}
        required={required}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy}
        {...props}
      />

      {helperText && !error && (
        <span id={helperId} className={styles.helper}>
          {helperText}
        </span>
      )}

      {error && (
        <span id={errorId} className={styles.error}>
          {error}
        </span>
      )}
    </label>
  );
}
