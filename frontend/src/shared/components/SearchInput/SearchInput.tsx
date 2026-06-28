import type { InputHTMLAttributes } from 'react';
import css from './SearchInput.module.css';

interface SearchInputProps extends InputHTMLAttributes<HTMLInputElement> {}

export function SearchInput(props: SearchInputProps) {
  return (
    <input
      className={css.input}
      type="search"
      {...props}
    />
  );
}