import { getMe } from '../../api/auth.ts';
import { InvalidUserResponseError, type User } from '../../api/userContract.ts';
import { ApiConfigurationError, ApiError, getToken, removeToken } from '../../api/client.ts';

export type CurrentUserFailure = 'forbidden' | 'malformed-response' | 'network' | 'server' | 'configuration' | 'unexpected';
export type CurrentUserSessionState =
  | { status: 'loading' }
  | { status: 'anonymous'; reason: 'missing-token' | 'expired-session' }
  | { status: 'authenticated'; user: User }
  | { status: 'error'; failure: CurrentUserFailure };

export type CurrentUserSessionDependencies = {
  readToken: () => string | null;
  readCurrentUser: () => Promise<User>;
  clearSession: () => void;
};

const defaultDependencies: CurrentUserSessionDependencies = {
  readToken: getToken,
  readCurrentUser: getMe,
  clearSession: removeToken,
};

export async function loadCurrentUserSession(
  dependencies: CurrentUserSessionDependencies = defaultDependencies,
  isRequestActive: () => boolean = () => true,
): Promise<CurrentUserSessionState> {
  if (!dependencies.readToken()) return { status: 'anonymous', reason: 'missing-token' };

  try {
    return { status: 'authenticated', user: await dependencies.readCurrentUser() };
  } catch (error: unknown) {
    if (error instanceof ApiError && error.kind === 'http' && error.status === 401) {
      if (isRequestActive()) dependencies.clearSession();
      return { status: 'anonymous', reason: 'expired-session' };
    }
    if (error instanceof ApiError && error.kind === 'http' && error.status === 403) return { status: 'error', failure: 'forbidden' };
    if (error instanceof InvalidUserResponseError) return { status: 'error', failure: 'malformed-response' };
    if (error instanceof ApiConfigurationError) return { status: 'error', failure: 'configuration' };
    if (error instanceof ApiError && error.kind === 'network') return { status: 'error', failure: 'network' };
    if (error instanceof ApiError && error.kind === 'http' && (error.status ?? 0) >= 500) return { status: 'error', failure: 'server' };
    return { status: 'error', failure: 'unexpected' };
  }
}

export type CurrentUserSessionRequest = {
  isActive: () => boolean;
  apply: (state: CurrentUserSessionState) => void;
};

export function createCurrentUserSessionRequestCoordinator(
  applyState: (state: CurrentUserSessionState) => void,
): { begin: () => CurrentUserSessionRequest; invalidate: () => void } {
  let activeGeneration = 0;

  return {
    begin: () => {
      const generation = ++activeGeneration;
      const isActive = () => generation === activeGeneration;
      return {
        isActive,
        apply: (state) => {
          if (isActive()) applyState(state);
        },
      };
    },
    invalidate: () => { activeGeneration += 1; },
  };
}

export type CurrentUserErrorView = { title: string; message: string };
const errorViews: Record<CurrentUserFailure, CurrentUserErrorView> = {
  forbidden: { title: 'Доступ заборонено', message: 'Ваш обліковий запис не має дозволу на отримання даних поточної сесії.' },
  'malformed-response': { title: 'Некоректна відповідь сервера', message: 'Сервер повернув неповні або некоректні дані користувача.' },
  network: { title: 'Немає зв’язку із сервером', message: 'Не вдалося перевірити поточну сесію. Перевірте мережеве з’єднання та повторіть спробу.' },
  server: { title: 'Помилка сервера', message: 'Сервер не зміг перевірити поточну сесію. Повторіть спробу пізніше.' },
  configuration: { title: 'Сервіс не налаштовано', message: 'Адресу сервера автентифікації налаштовано некоректно.' },
  unexpected: { title: 'Не вдалося перевірити сесію', message: 'Сталася неочікувана помилка. Повторіть спробу.' },
};

export function getCurrentUserErrorView(failure: CurrentUserFailure): CurrentUserErrorView {
  return errorViews[failure];
}

export function getCurrentUserDestination(state: CurrentUserSessionState): 'loading' | 'login' | 'application' | 'error' {
  if (state.status === 'anonymous') return 'login';
  if (state.status === 'authenticated') return 'application';
  return state.status;
}
