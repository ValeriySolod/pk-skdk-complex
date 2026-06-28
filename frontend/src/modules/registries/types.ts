export interface RegistryItem {
  id: string;
  title: string;
  description: string;
  path: string;
  status: 'active' | 'planned';
}

export interface RegistryRecord {
  id: number;
  number: string;
  sender_org_id: number;
  received_at: string;
  qr_payload: string | null;
  status: string;
}

export interface CreateRegistryPayload {
  number: string;
  sender_org_id: number;
  qr_payload?: string | null;
}