import type { ReactNode } from 'react';
import styles from './FormField.module.css';

export interface FormFieldProps {
  id: string;
  label?: ReactNode;
  helperText?: ReactNode;
  error?: ReactNode;
  required?: boolean;
  className?: string;
  children: ReactNode;
}

export function FormField({
  id,
  label,
  helperText,
  error,
  required,
  className = '',
  children,
}: FormFieldProps) {
  const helperTextId = `${id}-helper`;
  const errorId = `${id}-error`;

  return (
    <div className={`${styles.field} ${className}`}>
      {label && (
        <label className={styles.label} htmlFor={id}>
          {label}
          {required && <span className={styles.required}> *</span>}
        </label>
      )}

      {children}

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
