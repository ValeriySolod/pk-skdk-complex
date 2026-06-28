import type { SelectHTMLAttributes } from 'react';
import styles from './Select.module.css';

export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface SelectProps
  extends Omit<SelectHTMLAttributes<HTMLSelectElement>, 'children'> {
  label?: string;
  helperText?: string;
  error?: string;
  options: SelectOption[];
  placeholder?: string;
  readOnly?: boolean;
}

export function Select({
  id,
  label,
  helperText,
  error,
  options,
  placeholder,
  className = '',
  disabled,
  readOnly,
  required,
  onChange,
  onKeyDown,
  'aria-describedby': ariaDescribedBy,
  ...props
}: SelectProps) {
  const selectId = id ?? props.name;
  const helperTextId = helperText && selectId ? `${selectId}-helper` : undefined;
  const errorId = error && selectId ? `${selectId}-error` : undefined;

  const describedBy = [ariaDescribedBy, errorId, helperTextId].filter(Boolean).join(' ') || undefined;

  return (
    <div className={styles.field}>
      {label && (
        <label className={styles.label} htmlFor={selectId}>
          {label}
          {required && <span className={styles.required}> *</span>}
        </label>
      )}

      <select
        id={selectId}
        className={`${styles.select} ${error ? styles.error : ''} ${
          readOnly ? styles.readOnly : ''
        } ${className}`}
        disabled={disabled}
        required={required}
        aria-invalid={error ? 'true' : undefined}
        aria-describedby={describedBy}
        onChange={(event) => {
          if (readOnly) {
            event.preventDefault();
            return;
          }

          onChange?.(event);
        }}
        onKeyDown={(event) => {
          if (readOnly) {
            event.preventDefault();
            return;
          }

          onKeyDown?.(event);
        }}
        {...props}
      >
        {placeholder && (
          <option value="" disabled hidden>
            {placeholder}
          </option>
        )}

        {options.map((option) => (
          <option key={option.value} value={option.value} disabled={option.disabled}>
            {option.label}
          </option>
        ))}
      </select>

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