import test from 'node:test';
import assert from 'node:assert/strict';
import { getDemoPositions, getPositions, getRealPositions } from './positionsApi.ts';

test('real positions path uses the canonical relative API endpoint and validates its response', async () => {
  let path;
  const positions = await getRealPositions(async (requestedPath) => {
    path = requestedPath;
    return [{ id: 1, title: 'Inspector', code: null, organization_unit_id: 4, is_active: true }];
  });
  assert.equal(path, '/organization-structure/positions');
  assert.equal(positions[0].title, 'Inspector');
});

test('demo positions path is an explicit isolated mock and returns detached values', async () => {
  const first = await getDemoPositions();
  first[0].title = 'Changed by caller';
  const second = await getDemoPositions();
  assert.notEqual(second[0].title, 'Changed by caller');
});

test('public dispatcher uses demo data without invoking the canonical API request', async () => {
  let requestCount = 0;
  let demoCount = 0;
  const demoPositions = [{ id: 91, title: 'Demo Position', code: null, organization_unit_id: 1, is_active: true }];
  const result = await getPositions({
    demoMode: true,
    request: async () => { requestCount += 1; return []; },
    readDemoPositions: async () => { demoCount += 1; return demoPositions; },
  });
  assert.deepEqual(result, demoPositions);
  assert.equal(demoCount, 1);
  assert.equal(requestCount, 0);
});

test('public dispatcher uses the real canonical request path outside demo mode', async () => {
  let requestedPath;
  let demoCount = 0;
  const realPositions = [{ id: 7, title: 'Inspector', code: 'INSP', organization_unit_id: 2, is_active: true }];
  const result = await getPositions({
    demoMode: false,
    request: async (path) => { requestedPath = path; return realPositions; },
    readDemoPositions: async () => { demoCount += 1; return []; },
  });
  assert.deepEqual(result, realPositions);
  assert.equal(requestedPath, '/organization-structure/positions');
  assert.equal(demoCount, 0);
});
