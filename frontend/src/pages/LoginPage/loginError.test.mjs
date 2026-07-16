import test from 'node:test';
import assert from 'node:assert/strict';
import { ApiConfigurationError, ApiError } from '../../api/client.ts';
import { getLoginErrorMessage } from './loginError.ts';

test('login errors map to exact Ukrainian messages by typed category', () => {
  const cases = [
    [new ApiError('Unauthorized', 'http', 401), 'Невірний логін або пароль'],
    [new ApiError('Forbidden', 'http', 403), 'Доступ до системи заборонено'],
    [new ApiError('Validation failed', 'http', 422), 'Некоректний запит авторизації'],
    [new ApiError('Network failed', 'network'), 'Не вдалося з’єднатися із сервером'],
    [new ApiConfigurationError(), 'Сервіс авторизації не налаштовано'],
    [new ApiError('Server failed', 'http', 500), 'Не вдалося увійти. Спробуйте ще раз пізніше'],
    [new ApiError('Conflict', 'http', 409), 'Не вдалося увійти. Спробуйте ще раз пізніше'],
    [{ unexpected: true }, 'Не вдалося увійти. Спробуйте ще раз пізніше'],
  ];

  for (const [error, expectedMessage] of cases) {
    assert.equal(getLoginErrorMessage(error), expectedMessage);
  }
});
