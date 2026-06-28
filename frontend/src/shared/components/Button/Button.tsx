import type { ButtonHTMLAttributes, ReactNode } from 'react';
import css from './Button.module.css';

export type ButtonVariant = 'primary' | 'secondary' | 'danger';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: ButtonVariant;
}

export function Button({
  children,
  variant = 'primary',
  className = '',
  type = 'button',
  ...props
}: ButtonProps) {
  return (
    <button
      className={`${css.button} ${css[variant]} ${className}`}
      type={type}
      {...props}
    >
      {children}
    </button>
  );
}
