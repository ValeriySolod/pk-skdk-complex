import type { ReactNode } from 'react';

import { AccessDeniedPage } from '../../pages/AccessDeniedPage';
import { hasRequiredRole } from './hasRequiredRole';

export type RouteGuardProps = {
  children: ReactNode;
  userRole: string;
  allowedRoles?: string[];
};

export function RouteGuard({ children, userRole, allowedRoles }: RouteGuardProps) {
  const canAccessRoute = hasRequiredRole(userRole, allowedRoles);

  if (!canAccessRoute) {
    return <AccessDeniedPage />;
  }

  return <>{children}</>;
}
