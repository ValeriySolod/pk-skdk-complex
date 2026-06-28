import { Input } from '../Input';
import styles from './SearchBox.module.css';

type SearchBoxProps = {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
};

export function SearchBox({ value, onChange, placeholder = 'Пошук...' }: SearchBoxProps) {
  return (
    <div className={styles.searchBox}>
      <Input
        type="search"
        value={value}
        placeholder={placeholder}
        onChange={(event) => onChange(event.target.value)}
      />
    </div>
  );
}
