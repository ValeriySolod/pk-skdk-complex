import { FormEvent, useState } from 'react';
import { login } from '../../api/auth';
import css from './LoginPage.module.css';
import { getLoginErrorMessage } from './loginError';

interface LoginPageProps {
  onLogin: () => void;
}

export default function LoginPage({ onLogin }: LoginPageProps) {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin12345');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    try {
      setLoading(true);
      setError('');

      await login(username, password);
      onLogin();
    } catch (loginError: unknown) {
      setError(getLoginErrorMessage(loginError));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className={css.page}>
      <section className={css.card}>
        <h1 className={css.title}>ПК СКДК</h1>
        <p className={css.subtitle}>Вхід до системи контролю доставки кореспонденції</p>

        <form className={css.form} onSubmit={handleSubmit}>
          <label className={css.label}>
            Логін
            <input
              className={css.input}
              value={username}
              onChange={event => setUsername(event.target.value)}
              autoComplete="username"
            />
          </label>

          <label className={css.label}>
            Пароль
            <input
              className={css.input}
              type="password"
              value={password}
              onChange={event => setPassword(event.target.value)}
              autoComplete="current-password"
            />
          </label>

          {error && <p className={css.error}>{error}</p>}

          <button className={css.button} type="submit" disabled={loading}>
            {loading ? 'Вхід...' : 'Увійти'}
          </button>
        </form>
      </section>
    </main>
  );
}
