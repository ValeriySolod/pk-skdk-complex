export interface Organization {
  id: number;
  name: string;
  edrpou: string | null;
  address: string;
  responsible_person: string | null;
  phone: string | null;
}

export interface OrganizationCreateData {
  name: string;
  edrpou?: string | null;
  address: string;
  responsible_person?: string | null;
  phone?: string | null;
}

export interface OrganizationUpdateData {
  name?: string;
  edrpou?: string | null;
  address?: string;
  responsible_person?: string | null;
  phone?: string | null;
}