import React, { useCallback, useEffect, useMemo, useState } from 'react';
import ReactDOM from 'react-dom/client';
import { createBrowserRouter, Navigate, RouterProvider, useLocation } from 'react-router-dom';
import { ApplicationShell } from './app/ApplicationShell';
import { AuthGuard } from './app/guards';
import { HomePage } from './app/HomePage';
import { isModuleVisibleForRole, modules } from './app/moduleRegistry';
import LoginPage from './pages/LoginPage/LoginPage';
import { getMe, logout, type User } from './api/auth';
import { getToken } from './api/client';
import { ToastProvider } from './shared/ui';

type AppRouterProps = {
  user: User | null;
  onLogout: () => void;
  onLogin: () => void;
};

type LoginLocationState = {
  from?: {
    pathname: string;
    search: string;
    hash: string;
  };
};

type LoginRouteProps = {
  user: User | null;
  onLogin: () => void;
};

function getRedirectPath(state: LoginLocationState | null): string {
  const from = state?.from;

  if (!from) {
    return '/';
  }

  return `${from.pathname}${from.search}${from.hash}`;
}

function LoginRoute({ user, onLogin }: LoginRouteProps) {
  const location = useLocation();
  const redirectPath = getRedirectPath(location.state as LoginLocationState | null);

  if (user) {
    return <Navigate to={redirectPath} replace />;
  }

  return <LoginPage onLogin={onLogin} />;
}

function AppRouter({ user, onLogout, onLogin }: AppRouterProps) {
  const router = useMemo(
    () => {
      const routedModules = user
        ? modules.filter((module) => isModuleVisibleForRole(module, user.role))
        : modules;

      return createBrowserRouter([
        {
          path: '/login',
          element: <LoginRoute user={user} onLogin={onLogin} />,
        },
        {
          path: '/',
          element: (
            <AuthGuard isAuthenticated={user !== null}>
              {user ? <ApplicationShell user={user} onLogout={onLogout} /> : null}
            </AuthGuard>
          ),
          children: [
            { index: true, element: user ? <HomePage userRole={user.role} /> : null },
            ...routedModules.map(({ path, Component }) => ({
              path,
              element: <Component />,
            })),
          ],
        },
      ]);
    },
    [onLogin, onLogout, user],
  );

  return (
    <React.Suspense fallback={<p style={{ padding: 32 }}>Loading module...</p>}>
      <RouterProvider router={router} />
    </React.Suspense>
  );
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

  return <AppRouter user={user} onLogout={handleLogout} onLogin={checkAuth} />;
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ToastProvider>
      <Root />
    </ToastProvider>
  </React.StrictMode>,
);
