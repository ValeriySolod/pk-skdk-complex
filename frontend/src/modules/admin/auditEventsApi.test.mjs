import test from 'node:test';
import assert from 'node:assert/strict';
import { getAuditEvents, getDemoAuditEvents, getRealAuditEvents } from './auditEventsApi.ts';

const events = [{ id: 1, actor_user_id: null, target_user_id: 2, event_type: 'user.viewed', summary: null, details: { source: 'test' }, created_at: '2026-01-01T00:00:00Z' }];
test('real audit events path uses the canonical relative endpoint and validates its response', async () => { let path; assert.deepEqual(await getRealAuditEvents(async (requestedPath) => { path = requestedPath; return events; }), events); assert.equal(path, '/user-management/audit-events'); });
test('demo audit events path is an explicit isolated mock and returns detached values', async () => { const first = await getDemoAuditEvents(); first[0].event_type = 'changed'; assert.notEqual((await getDemoAuditEvents())[0].event_type, 'changed'); });
test('audit events dispatcher isolates demo and real request paths', async () => { let requestCount = 0; let demoCount = 0; assert.deepEqual(await getAuditEvents({ demoMode: true, request: async () => { requestCount += 1; return []; }, readDemoAuditEvents: async () => { demoCount += 1; return events; } }), events); assert.equal(requestCount, 0); assert.equal(demoCount, 1); let path; assert.deepEqual(await getAuditEvents({ demoMode: false, request: async (value) => { path = value; return events; }, readDemoAuditEvents: async () => [] }), events); assert.equal(path, '/user-management/audit-events'); });
