import type { InputHTMLAttributes } from 'react';
import css from './SearchInput.module.css';

export interface SearchInputProps extends InputHTMLAttributes<HTMLInputElement> {}

export function SearchInput({ className = '', type = 'search', ...props }: SearchInputProps) {
  return (
    <input
      className={`${css.input} ${className}`}
      type={type}
      {...props}
    />
  );
}
