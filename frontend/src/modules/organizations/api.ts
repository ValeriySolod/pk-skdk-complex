import { apiRequest } from '../../api/client';
import { IS_DEMO_MODE } from '../../shared/config';
import type {
  Organization,
  OrganizationCreateData,
  OrganizationUpdateData,
} from './types';

const BASE_URL = '/api/v1/organizations';

let demoOrganizations: Organization[] = [
  {
    id: 1,
    name: 'Тестова організація',
    edrpou: '00000000',
    address: 'м. Київ',
    responsible_person: 'Іваненко І.І.',
    phone: '0501234567',
  },
  {
    id: 2,
    name: 'Демо відправник',
    edrpou: '12345678',
    address: 'м. Львів',
    responsible_person: 'Петренко П.П.',
    phone: '0677654321',
  },
];

export async function getOrganizations(): Promise<Organization[]> {
  if (IS_DEMO_MODE) {
    return demoOrganizations;
  }

  return apiRequest<Organization[]>(BASE_URL);
}

export async function createOrganization(
  data: OrganizationCreateData
): Promise<Organization> {
  if (IS_DEMO_MODE) {
    const newOrganization: Organization = {
      id: Date.now(),
      name: data.name,
      edrpou: data.edrpou ?? null,
      address: data.address,
      responsible_person: data.responsible_person ?? null,
      phone: data.phone ?? null,
    };

    demoOrganizations = [newOrganization, ...demoOrganizations];

    return newOrganization;
  }

  return apiRequest<Organization>(BASE_URL, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateOrganization(
  id: number,
  data: OrganizationUpdateData
): Promise<Organization> {
  if (IS_DEMO_MODE) {
    demoOrganizations = demoOrganizations.map((org) =>
      org.id === id ? { ...org, ...data } : org
    );

    const updated = demoOrganizations.find((org) => org.id === id);

    if (!updated) {
      throw new Error('Organization not found');
    }

    return updated;
  }

  return apiRequest<Organization>(`${BASE_URL}/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteOrganization(id: number): Promise<void> {
  if (IS_DEMO_MODE) {
    demoOrganizations = demoOrganizations.filter((org) => org.id !== id);
    return;
  }

  return apiRequest<void>(`${BASE_URL}/${id}`, {
    method: 'DELETE',
  });
}