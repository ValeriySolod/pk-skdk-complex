import { IS_DEMO_MODE } from '../../../shared/config';
import { apiRequest } from '../../../api/client';
import type { CreateRegistryPayload, RegistryRecord } from '../types';

const demoRegistries: RegistryRecord[] = [
  {
    id: 1,
    number: 'ВХ-2026-001',
    sender_org_id: 1,
    received_at: new Date().toISOString(),
    qr_payload: 'PK-SKDK:REGISTRY:1',
    status: 'created',
  },
  {
    id: 2,
    number: 'ВХ-2026-002',
    sender_org_id: 2,
    received_at: new Date().toISOString(),
    qr_payload: 'PK-SKDK:REGISTRY:2',
    status: 'created',
  },
];

export async function fetchRegistries(): Promise<RegistryRecord[]> {
  if (IS_DEMO_MODE) {
    return demoRegistries;
  }

  return apiRequest<RegistryRecord[]>('/api/v1/registries');
}

export async function createRegistry(
  payload: CreateRegistryPayload
): Promise<RegistryRecord> {
  if (IS_DEMO_MODE) {
    return {
      id: Date.now(),
      number: payload.number,
      sender_org_id: payload.sender_org_id,
      received_at: new Date().toISOString(),
      qr_payload: payload.qr_payload ?? null,
      status: 'created',
    };
  }

  return apiRequest<RegistryRecord>('/api/v1/registries', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}