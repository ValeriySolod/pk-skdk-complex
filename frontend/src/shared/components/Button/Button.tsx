import type { ButtonHTMLAttributes, ReactNode } from 'react';
import css from './Button.module.css';

type ButtonVariant = 'primary' | 'secondary' | 'danger';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: ButtonVariant;
}

export function Button({
  children,
  variant = 'primary',
  className = '',
  ...props
}: ButtonProps) {
  return (
    <button
      className={`${css.button} ${css[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}