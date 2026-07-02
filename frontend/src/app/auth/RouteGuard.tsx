import type { ReactNode } from 'react';

import { hasRequiredRole } from './hasRequiredRole';

export type RouteGuardProps = {
  children: ReactNode;
  userRole: string;
  allowedRoles?: string[];
};

export function RouteGuard({ children, userRole, allowedRoles }: RouteGuardProps) {
  const canAccessRoute = hasRequiredRole(userRole, allowedRoles);

  if (!canAccessRoute) {
    return <p role="alert">Access denied</p>;
  }

  return <>{children}</>;
}
