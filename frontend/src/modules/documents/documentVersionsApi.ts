import { apiRequest } from '../../api/client.ts';
import { IS_DEMO_MODE } from '../../shared/config.ts';
import { parseDocumentVersions, type DocumentVersionRead } from './documentVersionContract.ts';

export type DocumentVersionsRequest = (path: string) => Promise<unknown>;
export type DocumentVersionsApiDependencies = {
  demoMode: boolean;
  request: DocumentVersionsRequest;
  readDemoDocumentVersions: (documentId: number) => Promise<DocumentVersionRead[]>;
};

const demoVersions: Record<number, DocumentVersionRead[]> = {
  1: [{ id: 1, document_id: 1, version: '1.0', file_name: 'quality-policy.pdf', storage_path: '/documents/quality-policy.pdf', checksum: null, uploaded_by: null, uploaded_at: '2026-01-01T00:00:00Z' }],
};

export async function getRealDocumentVersions(documentId: number, request: DocumentVersionsRequest = apiRequest): Promise<DocumentVersionRead[]> {
  return parseDocumentVersions(await request(`/document-management/documents/${documentId}/versions`));
}

export async function getDemoDocumentVersions(documentId: number): Promise<DocumentVersionRead[]> {
  return (demoVersions[documentId] ?? []).map((version) => ({ ...version }));
}

const defaults: DocumentVersionsApiDependencies = {
  demoMode: IS_DEMO_MODE,
  request: apiRequest,
  readDemoDocumentVersions: getDemoDocumentVersions,
};

export function getDocumentVersions(documentId: number, dependencies: DocumentVersionsApiDependencies = defaults): Promise<DocumentVersionRead[]> {
  return dependencies.demoMode
    ? dependencies.readDemoDocumentVersions(documentId)
    : getRealDocumentVersions(documentId, dependencies.request);
}
