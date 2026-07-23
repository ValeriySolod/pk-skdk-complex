import { ApiConfigurationError, ApiError, removeToken } from '../../api/client.ts';
import { InvalidDocumentCategoriesResponseError, type DocumentCategoryRead } from './documentCategoryContract.ts';
import { getDocumentCategories } from './documentCategoriesApi.ts';

export type DocumentCategoriesFailure = 'forbidden' | 'malformed-response' | 'network' | 'configuration' | 'server' | 'unexpected';
export type DocumentCategoriesState =
  | { status: 'loading' }
  | { status: 'success'; categories: DocumentCategoryRead[] }
  | { status: 'expired-session' }
  | { status: 'error'; failure: DocumentCategoriesFailure };
export type DocumentCategoriesDependencies = {
  readDocumentCategories: () => Promise<DocumentCategoryRead[]>;
  clearSession: () => void;
};

const defaults: DocumentCategoriesDependencies = { readDocumentCategories: getDocumentCategories, clearSession: removeToken };

export async function loadDocumentCategories(
  dependencies: DocumentCategoriesDependencies = defaults,
  isRequestActive: () => boolean = () => true,
): Promise<DocumentCategoriesState> {
  try {
    return { status: 'success', categories: await dependencies.readDocumentCategories() };
  } catch (error: unknown) {
    if (error instanceof ApiError && error.kind === 'http' && error.status === 401) {
      if (isRequestActive()) dependencies.clearSession();
      return { status: 'expired-session' };
    }
    if (error instanceof ApiError && error.kind === 'http' && error.status === 403) return { status: 'error', failure: 'forbidden' };
    if (error instanceof InvalidDocumentCategoriesResponseError) return { status: 'error', failure: 'malformed-response' };
    if (error instanceof ApiConfigurationError) return { status: 'error', failure: 'configuration' };
    if (error instanceof ApiError && error.kind === 'network') return { status: 'error', failure: 'network' };
    if (error instanceof ApiError && error.kind === 'http' && (error.status ?? 0) >= 500) return { status: 'error', failure: 'server' };
    return { status: 'error', failure: 'unexpected' };
  }
}

export const documentCategoriesErrorMessages: Record<DocumentCategoriesFailure, string> = {
  forbidden: 'You do not have permission to view document categories.',
  'malformed-response': 'The server returned an invalid document categories response.',
  network: 'The server could not be reached. Check the network connection and retry.',
  configuration: 'The backend API address is not configured correctly.',
  server: 'The server could not load document categories. Retry later.',
  unexpected: 'Document categories could not be loaded. Retry the request.',
};
