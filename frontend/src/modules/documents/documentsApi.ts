import { apiRequest } from '../../api/client.ts';
import { IS_DEMO_MODE } from '../../shared/config.ts';
import { parseDocuments, type DocumentRead } from './documentContract.ts';
const DOCUMENTS_PATH = '/document-management/documents';
const demoDocuments: DocumentRead[] = [{ id: 1, title: 'Quality policy', document_number: 'DOC-001', description: null, document_type: 'policy', status: 'active', organization_id: null, owner_user_id: null, created_at: '2026-01-01T00:00:00Z', updated_at: '2026-01-01T00:00:00Z' }];
export type DocumentsRequest = (path: string) => Promise<unknown>;
export type DocumentsApiDependencies = { demoMode: boolean; request: DocumentsRequest; readDemoDocuments: () => Promise<DocumentRead[]> };
export async function getRealDocuments(request: DocumentsRequest = apiRequest): Promise<DocumentRead[]> { return parseDocuments(await request(DOCUMENTS_PATH)); }
export async function getDemoDocuments(): Promise<DocumentRead[]> { return demoDocuments.map((document) => ({ ...document })); }
const defaults: DocumentsApiDependencies = { demoMode: IS_DEMO_MODE, request: apiRequest, readDemoDocuments: getDemoDocuments };
export function getDocuments(dependencies: DocumentsApiDependencies = defaults): Promise<DocumentRead[]> { return dependencies.demoMode ? dependencies.readDemoDocuments() : getRealDocuments(dependencies.request); }
