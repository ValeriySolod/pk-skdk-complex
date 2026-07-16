import test from 'node:test';
import assert from 'node:assert/strict';
import { ApiConfigurationError, ApiError, apiRequest, resolveApiBaseUrl } from './client.ts';

test('configuration accepts and normalizes HTTP(S) API roots', () => {
  assert.equal(resolveApiBaseUrl({ VITE_API_URL: 'http://localhost:8000/api/v1' }), 'http://localhost:8000/api/v1');
  assert.equal(resolveApiBaseUrl({ VITE_API_URL: 'https://api.example.test/api/v1/' }), 'https://api.example.test/api/v1');
});

test('configuration rejects unsafe or incorrectly scoped URLs', () => {
  const invalidValues = [
    undefined,
    '',
    'relative/api/v1',
    'ftp://api.example.test/api/v1',
    'https://user:password@api.example.test/api/v1',
    'https://api.example.test/api/v1?tenant=one',
    'https://api.example.test/api/v1#section',
    'https://api.example.test/',
    'https://api.example.test/api/v2',
  ];
  for (const value of invalidValues) {
    assert.throws(
      () => resolveApiBaseUrl({ VITE_API_URL: value }),
      (error) => error instanceof ApiConfigurationError,
    );
  }
});

test('request configuration failures remain distinct from network errors', async () => {
  await assert.rejects(
    apiRequest('/health', {}, { token: () => null }),
    (error) => error instanceof ApiConfigurationError,
  );
});

test('successful JSON requests use the normalized URL and bearer authentication', async () => {
  let requestedUrl;
  let headers;
  const request = async (url, init) => {
    requestedUrl = url;
    headers = new Headers(init.headers);
    return new Response(JSON.stringify({ ok: true }), { status: 200 });
  };
  const result = await apiRequest('/health', {}, {
    baseUrl: 'https://api.example.test/api/v1/', fetch: request, token: () => 'test-token',
  });
  assert.deepEqual(result, { ok: true });
  assert.equal(requestedUrl, 'https://api.example.test/api/v1/health');
  assert.equal(headers.get('Authorization'), 'Bearer test-token');
});

test('explicitly unauthenticated requests omit bearer authentication', async () => {
  let headers;
  const request = async (_url, init) => {
    headers = new Headers(init.headers);
    return new Response(null, { status: 204 });
  };
  const result = await apiRequest('/auth/logout', { method: 'POST' }, {
    baseUrl: 'https://api.example.test/api/v1', fetch: request, token: () => null,
  });
  assert.equal(result, undefined);
  assert.equal(headers.has('Authorization'), false);
});

test('FastAPI validation responses preserve status and deeply equal detail', async () => {
  const detail = [{ loc: ['body', 'name'], msg: 'Field required', type: 'missing' }];
  const request = async () => new Response(JSON.stringify({ detail }), { status: 422 });
  await assert.rejects(
    apiRequest('/items', {}, { baseUrl: 'https://api.example.test/api/v1', fetch: request, token: () => null }),
    (error) => {
      if (!(error instanceof ApiError)) return false;
      assert.equal(error.kind, 'http');
      assert.equal(error.status, 422);
      assert.deepEqual(error.detail, detail);
      return true;
    },
  );
});

test('network failures are deterministic and do not expose low-level text', async () => {
  const sensitiveText = 'transport included a sensitive credential';
  const request = async () => { throw new Error(sensitiveText); };
  await assert.rejects(
    apiRequest('/items', {}, { baseUrl: 'https://api.example.test/api/v1', fetch: request, token: () => 'test-token' }),
    (error) => error instanceof ApiError && error.kind === 'network' && !error.message.includes(sensitiveText),
  );
});
