import type { InputHTMLAttributes } from 'react';
import { Input } from '../../ui/Input';

interface SearchInputProps extends InputHTMLAttributes<HTMLInputElement> {}

export function SearchInput(props: SearchInputProps) {
  return <Input type="search" {...props} />;
}
