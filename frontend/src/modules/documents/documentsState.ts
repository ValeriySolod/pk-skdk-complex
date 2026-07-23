import { ApiConfigurationError, ApiError, removeToken } from '../../api/client.ts';
import { InvalidDocumentsResponseError, type DocumentRead } from './documentContract.ts';
import { getDocuments } from './documentsApi.ts';
export type DocumentsFailure = 'forbidden' | 'malformed-response' | 'network' | 'configuration' | 'server' | 'unexpected';
export type DocumentsState = { status: 'loading' } | { status: 'success'; documents: DocumentRead[] } | { status: 'expired-session' } | { status: 'error'; failure: DocumentsFailure };
export type DocumentsDependencies = { readDocuments: () => Promise<DocumentRead[]>; clearSession: () => void };
const defaults: DocumentsDependencies = { readDocuments: getDocuments, clearSession: removeToken };
export async function loadDocuments(dependencies: DocumentsDependencies = defaults, isRequestActive: () => boolean = () => true): Promise<DocumentsState> {
  try { return { status: 'success', documents: await dependencies.readDocuments() }; } catch (error: unknown) {
    if (error instanceof ApiError && error.kind === 'http' && error.status === 401) { if (isRequestActive()) dependencies.clearSession(); return { status: 'expired-session' }; }
    if (error instanceof ApiError && error.kind === 'http' && error.status === 403) return { status: 'error', failure: 'forbidden' };
    if (error instanceof InvalidDocumentsResponseError) return { status: 'error', failure: 'malformed-response' };
    if (error instanceof ApiConfigurationError) return { status: 'error', failure: 'configuration' };
    if (error instanceof ApiError && error.kind === 'network') return { status: 'error', failure: 'network' };
    if (error instanceof ApiError && error.kind === 'http' && (error.status ?? 0) >= 500) return { status: 'error', failure: 'server' };
    return { status: 'error', failure: 'unexpected' };
  }
}
export const documentsErrorMessages: Record<DocumentsFailure, string> = {
  forbidden: 'You do not have permission to view documents.', 'malformed-response': 'The server returned an invalid documents response.',
  network: 'The server could not be reached. Check the network connection and retry.', configuration: 'The backend API address is not configured correctly.',
  server: 'The server could not load documents. Retry later.', unexpected: 'Documents could not be loaded. Retry the request.',
};
