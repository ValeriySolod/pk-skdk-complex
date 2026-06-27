import styles from './EmptyState.module.css';

type EmptyStateProps = {
  text: string;
};

export function EmptyState({ text }: EmptyStateProps) {
  return <div className={styles.empty}>{text}</div>;
}