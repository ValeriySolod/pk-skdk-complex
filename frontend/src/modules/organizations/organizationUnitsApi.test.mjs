import test from 'node:test';
import assert from 'node:assert/strict';
import { getDemoOrganizationUnits, getOrganizationUnits, getRealOrganizationUnits } from './organizationUnitsApi.ts';

test('real organization-units path uses the canonical relative API endpoint and validates its response', async () => {
  let path;
  const units = await getRealOrganizationUnits(async (requestedPath) => {
    path = requestedPath;
    return [{ id: 1, name: 'Head Office', code: null, parent_id: null, is_active: true }];
  });
  assert.equal(path, '/organization-structure/units');
  assert.equal(units[0].name, 'Head Office');
});

test('demo organization-units path is an explicit isolated mock and returns detached values', async () => {
  const first = await getDemoOrganizationUnits();
  first[0].name = 'Changed by caller';
  const second = await getDemoOrganizationUnits();
  assert.notEqual(second[0].name, 'Changed by caller');
});

test('public dispatcher uses demo data without invoking the canonical API request', async () => {
  let requestCount = 0;
  let demoCount = 0;
  const demoUnits = [{ id: 91, name: 'Demo Unit', code: null, parent_id: null, is_active: true }];

  const result = await getOrganizationUnits({
    demoMode: true,
    request: async () => { requestCount += 1; return []; },
    readDemoUnits: async () => { demoCount += 1; return demoUnits; },
  });

  assert.deepEqual(result, demoUnits);
  assert.equal(demoCount, 1);
  assert.equal(requestCount, 0);
});

test('public dispatcher uses the real canonical request path outside demo mode', async () => {
  let requestedPath;
  let demoCount = 0;
  const realUnits = [{ id: 7, name: 'Operations', code: 'OPS', parent_id: null, is_active: true }];

  const result = await getOrganizationUnits({
    demoMode: false,
    request: async (path) => { requestedPath = path; return realUnits; },
    readDemoUnits: async () => { demoCount += 1; return []; },
  });

  assert.deepEqual(result, realUnits);
  assert.equal(requestedPath, '/organization-structure/units');
  assert.equal(demoCount, 0);
});
