import type { ReactNode } from 'react';

export type AuthGuardProps = {
  children: ReactNode;
};

export function AuthGuard({ children }: AuthGuardProps) {
  return <>{children}</>;
}
