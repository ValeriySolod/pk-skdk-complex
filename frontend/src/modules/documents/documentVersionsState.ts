import { ApiConfigurationError, ApiError, removeToken } from '../../api/client.ts';
import { InvalidDocumentVersionsResponseError, type DocumentVersionRead } from './documentVersionContract.ts';
import { getDocumentVersions } from './documentVersionsApi.ts';

export type DocumentVersionsFailure = 'forbidden' | 'malformed-response' | 'network' | 'configuration' | 'server' | 'unexpected';
export type DocumentVersionsState =
  | { status: 'unselected' }
  | { status: 'loading'; documentId: number }
  | { status: 'success'; documentId: number; versions: DocumentVersionRead[] }
  | { status: 'expired-session'; documentId: number }
  | { status: 'error'; documentId: number; failure: DocumentVersionsFailure };
export type DocumentVersionsDependencies = {
  readDocumentVersions: (documentId: number) => Promise<DocumentVersionRead[]>;
  clearSession: () => void;
};

const defaults: DocumentVersionsDependencies = { readDocumentVersions: getDocumentVersions, clearSession: removeToken };

export async function loadDocumentVersions(
  documentId: number,
  dependencies: DocumentVersionsDependencies = defaults,
  isRequestActive: () => boolean = () => true,
): Promise<DocumentVersionsState> {
  try {
    return { status: 'success', documentId, versions: await dependencies.readDocumentVersions(documentId) };
  } catch (error: unknown) {
    if (error instanceof ApiError && error.kind === 'http' && error.status === 401) {
      if (isRequestActive()) dependencies.clearSession();
      return { status: 'expired-session', documentId };
    }
    if (error instanceof ApiError && error.kind === 'http' && error.status === 403) return { status: 'error', documentId, failure: 'forbidden' };
    if (error instanceof InvalidDocumentVersionsResponseError) return { status: 'error', documentId, failure: 'malformed-response' };
    if (error instanceof ApiConfigurationError) return { status: 'error', documentId, failure: 'configuration' };
    if (error instanceof ApiError && error.kind === 'network') return { status: 'error', documentId, failure: 'network' };
    if (error instanceof ApiError && error.kind === 'http' && (error.status ?? 0) >= 500) return { status: 'error', documentId, failure: 'server' };
    return { status: 'error', documentId, failure: 'unexpected' };
  }
}

export const documentVersionsErrorMessages: Record<DocumentVersionsFailure, string> = {
  forbidden: 'You do not have permission to view document versions.',
  'malformed-response': 'The server returned an invalid document versions response.',
  network: 'The server could not be reached. Check the network connection and retry.',
  configuration: 'The backend API address is not configured correctly.',
  server: 'The server could not load document versions. Retry later.',
  unexpected: 'Document versions could not be loaded. Retry the request.',
};
