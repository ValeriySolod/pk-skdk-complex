import React, { useCallback, useEffect, useMemo, useState } from 'react';
import ReactDOM from 'react-dom/client';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { ApplicationShell } from './app/ApplicationShell';
import { AuthGuard } from './app/guards';
import { HomePage } from './app/HomePage';
import { modules } from './app/moduleRegistry';
import LoginPage from './pages/LoginPage/LoginPage';
import { getMe, logout, type User } from './api/auth';
import { getToken } from './api/client';
import { ToastProvider } from './shared/ui';

type AppRouterProps = {
  user: User;
  onLogout: () => void;
};

function AppRouter({ user, onLogout }: AppRouterProps) {
  const router = useMemo(
    () =>
      createBrowserRouter([
        {
          path: '/',
          element: (
            <AuthGuard>
              <ApplicationShell user={user} onLogout={onLogout} />
            </AuthGuard>
          ),
          children: [
            { index: true, element: <HomePage /> },
            ...modules.map(({ path, Component }) => ({
              path,
              element: <Component />,
            })),
          ],
        },
      ]),
    [onLogout, user],
  );

  return <RouterProvider router={router} />;
}

function Root() {
  const [user, setUser] = useState<User | null>(null);
  const [checkingAuth, setCheckingAuth] = useState(true);

  async function checkAuth() {
    try {
      const token = getToken();

      if (!token) {
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

  const handleLogout = useCallback(() => {
    logout();
    setUser(null);
  }, []);

  if (checkingAuth) {
    return <p style={{ padding: 32 }}>Перевірка авторизації...</p>;
  }

  if (!user) {
    return <LoginPage onLogin={checkAuth} />;
  }

  return <AppRouter user={user} onLogout={handleLogout} />;
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ToastProvider>
      <Root />
    </ToastProvider>
  </React.StrictMode>,
);
