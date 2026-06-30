import { forwardRef, type InputHTMLAttributes } from 'react';
import clsx from 'clsx';
import styles from './Input.module.css';

export interface InputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size'> {
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'filled';
  invalid?: boolean;
  fullWidth?: boolean;
  className?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      size = 'md',
      variant = 'default',
      invalid = false,
      fullWidth = false,
      className,
      'aria-invalid': ariaInvalid,
      ...props
    },
    ref
  ) => (
    <input
      ref={ref}
      className={clsx(
        styles.input,
        styles[size],
        styles[variant],
        invalid && styles.invalid,
        fullWidth && styles.fullWidth,
        className
      )}
      aria-invalid={invalid ? 'true' : ariaInvalid}
      {...props}
    />
  )
);

Input.displayName = 'Input';
