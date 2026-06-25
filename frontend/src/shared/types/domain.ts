export type ModuleManifest = {
  code: string;
  title: string;
  description: string;
  permissions: string[];
};

export type Shipment = {
  id: number;
  barcode: string;
  recipient_name: string;
  recipient_address: string;
  document_number?: string | null;
  access_mark: string;
  region?: string | null;
  district?: string | null;
  status: string;
};
