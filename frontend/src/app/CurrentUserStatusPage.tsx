import { getCurrentUserErrorView, type CurrentUserFailure } from './auth/currentUserSession';
import styles from './CurrentUserStatusPage.module.css';

export type CurrentUserStatusPageProps = {
  failure: CurrentUserFailure;
  onRetry: () => void;
  onLogout: () => void;
};

export function CurrentUserStatusPage({ failure, onRetry, onLogout }: CurrentUserStatusPageProps) {
  const view = getCurrentUserErrorView(failure);
  return (
    <main className={styles.page}>
      <section className={styles.card} aria-labelledby="session-status-title">
        <h1 id="session-status-title" className={styles.title}>{view.title}</h1>
        <p className={styles.message}>{view.message}</p>
        <div className={styles.actions}>
          <button className={styles.primaryButton} type="button" onClick={onRetry}>Повторити</button>
          <button className={styles.secondaryButton} type="button" onClick={onLogout}>Вийти</button>
        </div>
      </section>
    </main>
  );
}
