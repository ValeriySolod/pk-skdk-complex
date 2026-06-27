import styles from './Loader.module.css';

type LoaderProps = {
  text?: string;
};

export function Loader({ text = 'Завантаження...' }: LoaderProps) {
  return <div className={styles.loader}>{text}</div>;
}