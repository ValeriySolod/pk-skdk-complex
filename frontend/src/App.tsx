import { useEffect, useState } from 'react';
import LoginPage from './pages/LoginPage/LoginPage';
import { getMe, logout, User } from './api/auth';
import { getToken } from './api/client';

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [checkingAuth, setCheckingAuth] = useState(true);

  async function checkAuth() {
    try {
      if (!getToken()) {
        setUser(null);
        return;
      }

      const currentUser = await getMe();
      setUser(currentUser);
    } catch {
      logout();
      setUser(null);
    } finally {
      setCheckingAuth(false);
    }
  }

  useEffect(() => {
    checkAuth();
  }, []);

  function handleLogout() {
    logout();
    setUser(null);
  }

  if (checkingAuth) {
    return <p style={{ padding: 32 }}>Перевірка авторизації...</p>;
  }

  if (!user) {
    return <LoginPage onLogin={checkAuth} />;
  }

  return (
    <>
      {/* тут залишаєш твій поточний інтерфейс ПК СКДК */}

      <button onClick={handleLogout}>
        Вийти
      </button>
    </>
  );
}

export default App;