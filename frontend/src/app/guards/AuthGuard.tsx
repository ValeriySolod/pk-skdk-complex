import type { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';

export type AuthGuardProps = {
  children: ReactNode;
  isAuthenticated: boolean;
};

export function AuthGuard({ children, isAuthenticated }: AuthGuardProps) {
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <>{children}</>;
}
