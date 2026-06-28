import type React from 'react';
import styles from './RadioGroup.module.css';

export interface RadioGroupOption {
  value: string;
  label: React.ReactNode;
  helperText?: React.ReactNode;
  disabled?: boolean;
}

export interface RadioGroupProps
  extends Omit<React.FieldsetHTMLAttributes<HTMLFieldSetElement>, 'onChange'> {
  name: string;
  options: RadioGroupOption[];
  label?: React.ReactNode;
  helperText?: React.ReactNode;
  error?: React.ReactNode;
  value?: string;
  defaultValue?: string;
  required?: boolean;
  orientation?: 'vertical' | 'horizontal';
  onChange?: (value: string, event: React.ChangeEvent<HTMLInputElement>) => void;
}

export function RadioGroup({
  id,
  name,
  options,
  label,
  helperText,
  error,
  value,
  defaultValue,
  required,
  orientation = 'vertical',
  className = '',
  disabled,
  'aria-describedby': ariaDescribedBy,
  onChange,
  ...props
}: RadioGroupProps) {
  const groupId = id ?? name;
  const helperTextId = helperText ? `${groupId}-helper` : undefined;
  const errorId = error ? `${groupId}-error` : undefined;

  const describedBy = [ariaDescribedBy, errorId, !error ? helperTextId : undefined]
    .filter(Boolean)
    .join(' ') || undefined;

  const isControlled = value !== undefined;

  return (
    <fieldset
      id={groupId}
      className={`${styles.group} ${styles[orientation]} ${disabled ? styles.disabled : ''} ${className}`}
      disabled={disabled}
      aria-invalid={error ? 'true' : undefined}
      aria-describedby={describedBy}
      {...props}
    >
      {label && (
        <legend className={styles.legend}>
          {label}
          {required && <span className={styles.required}> *</span>}
        </legend>
      )}

      <div className={styles.options}>
        {options.map((option) => {
          const optionId = `${groupId}-${option.value}`;
          const optionHelperTextId = option.helperText ? `${optionId}-helper` : undefined;

          return (
            <div className={styles.option} key={option.value}>
              <div className={styles.controlRow}>
                <input
                  id={optionId}
                  className={`${styles.radio} ${error ? styles.errorState : ''}`}
                  type="radio"
                  name={name}
                  value={option.value}
                  required={required}
                  disabled={option.disabled}
                  checked={isControlled ? value === option.value : undefined}
                  defaultChecked={!isControlled ? defaultValue === option.value : undefined}
                  aria-invalid={error ? 'true' : undefined}
                  aria-describedby={optionHelperTextId}
                  onChange={(event) => onChange?.(event.target.value, event)}
                />

                <label className={styles.label} htmlFor={optionId}>
                  {option.label}
                </label>
              </div>

              {option.helperText && (
                <p className={styles.optionHelper} id={optionHelperTextId}>
                  {option.helperText}
                </p>
              )}
            </div>
          );
        })}
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
    </fieldset>
  );
}
