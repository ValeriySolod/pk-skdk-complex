import test from 'node:test';
import assert from 'node:assert/strict';
import { getDemoProfiles, getProfiles, getRealProfiles } from './profilesApi.ts';

const profiles = [{ id: 1, user_id: 2, display_name: null, personnel_number: null, job_title: null, phone_number: null, is_active: true, notes: null, created_at: '2026-01-01T00:00:00Z', updated_at: '2026-01-01T00:00:00Z' }];
test('real profiles path uses the canonical relative endpoint and validates its response', async () => { let path; assert.deepEqual(await getRealProfiles(async (requestedPath) => { path = requestedPath; return profiles; }), profiles); assert.equal(path, '/user-management/profiles'); });
test('demo profiles path is an explicit isolated mock and returns detached values', async () => { const first = await getDemoProfiles(); first[0].display_name = 'changed'; assert.notEqual((await getDemoProfiles())[0].display_name, 'changed'); });
test('profiles dispatcher isolates demo and real request paths', async () => { let requestCount = 0; let demoCount = 0; assert.deepEqual(await getProfiles({ demoMode: true, request: async () => { requestCount += 1; return []; }, readDemoProfiles: async () => { demoCount += 1; return profiles; } }), profiles); assert.equal(requestCount, 0); assert.equal(demoCount, 1); let path; assert.deepEqual(await getProfiles({ demoMode: false, request: async (value) => { path = value; return profiles; }, readDemoProfiles: async () => [] }), profiles); assert.equal(path, '/user-management/profiles'); });
