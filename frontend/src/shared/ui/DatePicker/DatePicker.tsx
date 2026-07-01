import { useId, type ChangeEvent } from 'react';
import clsx from 'clsx';

import styles from './DatePicker.module.css';

export interface DatePickerProps {
  value?: Date | null;
  onChange: (date: Date | null) => void;
  minDate?: Date;
  maxDate?: Date;
  disabled?: boolean;
  placeholder?: string;
  label?: string;
  error?: string;
  helperText?: string;
  className?: string;
  id?: string;
  name?: string;
}

export function DatePicker({
  value,
  onChange,
  minDate,
  maxDate,
  disabled = false,
  placeholder,
  label,
  error,
  helperText,
  className,
  id,
  name,
}: DatePickerProps) {
  const generatedId = useId();
  const inputId = id ?? generatedId;
  const helperTextId = `${inputId}-helper`;
  const errorId = `${inputId}-error`;
  const describedBy = error ? errorId : helperText ? helperTextId : undefined;

  function handleChange(event: ChangeEvent<HTMLInputElement>) {
    onChange(parseDateValue(event.target.value));
  }

  return (
    <div className={clsx(styles.field, className)}>
      {label ? (
        <label className={styles.label} htmlFor={inputId}>
          {label}
        </label>
      ) : null}

      <input
        className={clsx(styles.input, error && styles.invalid)}
        id={inputId}
        name={name}
        type="date"
        value={formatDateValue(value)}
        min={formatDateValue(minDate)}
        max={formatDateValue(maxDate)}
        disabled={disabled}
        placeholder={placeholder}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy}
        onChange={handleChange}
      />

      {error ? (
        <p className={styles.error} id={errorId}>
          {error}
        </p>
      ) : helperText ? (
        <p className={styles.helperText} id={helperTextId}>
          {helperText}
        </p>
      ) : null}
    </div>
  );
}

function formatDateValue(date: Date | null | undefined) {
  if (!date) {
    return '';
  }

  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');

  return `${year}-${month}-${day}`;
}

function parseDateValue(value: string) {
  if (!value) {
    return null;
  }

  const [yearValue, monthValue, dayValue] = value.split('-');
  const year = Number(yearValue);
  const month = Number(monthValue);
  const day = Number(dayValue);

  if (!year || !month || !day) {
    return null;
  }

  return new Date(year, month - 1, day);
}
