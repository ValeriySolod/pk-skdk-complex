import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import ReactDOM from 'react-dom/client';
import { createBrowserRouter, Navigate, RouterProvider, useLocation } from 'react-router-dom';
import { ApplicationShell } from './app/ApplicationShell';
import { CurrentUserStatusPage } from './app/CurrentUserStatusPage';
import { RouteGuard } from './app/auth/RouteGuard';
import {
  createCurrentUserSessionRequestCoordinator,
  loadCurrentUserSession,
  type CurrentUserSessionState,
} from './app/auth/currentUserSession';
import { AuthGuard } from './app/guards';
import { HomePage } from './app/HomePage';
import { isModuleVisibleForRole, modules } from './app/moduleRegistry';
import LoginPage from './pages/LoginPage/LoginPage';
import { logout, type User } from './api/auth';
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
            ...routedModules.map(({ path, Component, roles }) => ({
              path,
              element: user ? (
                <RouteGuard userRole={user.role} allowedRoles={roles ? [...roles] : undefined}>
                  <Component />
                </RouteGuard>
              ) : null,
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
  const [session, setSession] = useState<CurrentUserSessionState>({ status: 'loading' });
  const requestCoordinator = useRef(createCurrentUserSessionRequestCoordinator(setSession));

  async function checkAuth() {
    const request = requestCoordinator.current.begin();
    setSession({ status: 'loading' });
    const nextSession = await loadCurrentUserSession(undefined, request.isActive);
    request.apply(nextSession);
  }

  useEffect(() => {
    checkAuth();
  }, []);

  const handleLogout = useCallback(() => {
    requestCoordinator.current.invalidate();
    logout();
    setSession({ status: 'anonymous', reason: 'missing-token' });
  }, []);

  if (session.status === 'loading') {
    return <p role="status" style={{ padding: 32 }}>Перевірка авторизації...</p>;
  }

  if (session.status === 'error') {
    return <CurrentUserStatusPage failure={session.failure} onRetry={checkAuth} onLogout={handleLogout} />;
  }

  const user = session.status === 'authenticated' ? session.user : null;
  return <AppRouter user={user} onLogout={handleLogout} onLogin={checkAuth} />;
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ToastProvider>
      <Root />
    </ToastProvider>
  </React.StrictMode>,
);
