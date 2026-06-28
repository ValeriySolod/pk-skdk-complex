import { FormEvent, useState } from 'react';
import { login } from '../../api/auth';
import { Input } from '../../shared/ui';
import css from './LoginPage.module.css';

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
    } catch {
      setError('Невірний логін або пароль');
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
          <Input
            label="Логін"
            value={username}
            onChange={event => setUsername(event.target.value)}
            autoComplete="username"
          />

          <Input
            label="Пароль"
            type="password"
            value={password}
            onChange={event => setPassword(event.target.value)}
            autoComplete="current-password"
          />

          {error && <p className={css.error}>{error}</p>}

          <button className={css.button} type="submit" disabled={loading}>
            {loading ? 'Вхід...' : 'Увійти'}
          </button>
        </form>
      </section>
    </main>
  );
}