import type { TextareaHTMLAttributes } from 'react';
import styles from './Textarea.module.css';

export interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  helperText?: string;
  error?: string;
}

export function Textarea({
  id,
  label,
  helperText,
  error,
  className = '',
  required,
  'aria-describedby': ariaDescribedBy,
  ...props
}: TextareaProps) {
  const textareaId = id ?? props.name;
  const helperTextId = helperText && textareaId ? `${textareaId}-helper` : undefined;
  const errorId = error && textareaId ? `${textareaId}-error` : undefined;

  const describedBy = [ariaDescribedBy, errorId, !error ? helperTextId : undefined]
    .filter(Boolean)
    .join(' ') || undefined;

  return (
    <div className={styles.field}>
      {label && (
        <label className={styles.label} htmlFor={textareaId}>
          {label}
          {required && <span className={styles.required}> *</span>}
        </label>
      )}

      <textarea
        id={textareaId}
        className={`${styles.textarea} ${error ? styles.error : ''} ${className}`}
        required={required}
        aria-invalid={error ? 'true' : undefined}
        aria-describedby={describedBy}
        {...props}
      />

      {error && (
        <p className={styles.errorText} id={errorId}>
          {error}
        </p>
      )}

      {!error && helperText && (
        <p className={styles.helperText} id={helperTextId}>
          {helperText}
        </p>
      )}
    </div>
  );
}
