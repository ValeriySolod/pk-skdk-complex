import React, { useEffect, useState } from 'react';
import ReactDOM from 'react-dom/client';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { Layout } from './components/Layout/Layout';
import { HomePage } from './app/HomePage';
import { modules } from './app/moduleRegistry';
import LoginPage from './pages/LoginPage/LoginPage';
import { getMe, logout, type User } from './api/auth';
import { getToken } from './api/client';

const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <HomePage /> },
      ...modules.map(({ path, Component }) => ({
        path,
        element: <Component />,
      })),
    ],
  },
]);

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

  if (checkingAuth) {
    return <p style={{ padding: 32 }}>Перевірка авторизації...</p>;
  }

  if (!user) {
    return <LoginPage onLogin={checkAuth} />;
  }

  return <RouterProvider router={router} />;
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>,
);
