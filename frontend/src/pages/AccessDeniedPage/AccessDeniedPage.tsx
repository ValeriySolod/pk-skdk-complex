import { Link } from 'react-router-dom';

import styles from './AccessDeniedPage.module.css';

export function AccessDeniedPage() {
  return (
    <main className={styles.page} aria-labelledby="access-denied-title">
      <section className={styles.content}>
        <p className={styles.status} role="alert">
          403
        </p>
        <h1 className={styles.title} id="access-denied-title">
          Доступ заборонено
        </h1>
        <p className={styles.message}>У вас немає прав для перегляду цього розділу.</p>
        <Link className={styles.action} to="/">
          Повернутися на головну
        </Link>
      </section>
    </main>
  );
}
