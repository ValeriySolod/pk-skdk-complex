import { ApiConfigurationError, ApiError } from '../../api/client.ts';

export function getLoginErrorMessage(error: unknown): string {
  if (error instanceof ApiConfigurationError) {
    return 'Сервіс авторизації не налаштовано';
  }

  if (error instanceof ApiError) {
    if (error.kind === 'network') return 'Не вдалося з’єднатися із сервером';
    if (error.status === 401) return 'Невірний логін або пароль';
    if (error.status === 403) return 'Доступ до системи заборонено';
    if (error.status === 422) return 'Некоректний запит авторизації';
  }

  return 'Не вдалося увійти. Спробуйте ще раз пізніше';
}
