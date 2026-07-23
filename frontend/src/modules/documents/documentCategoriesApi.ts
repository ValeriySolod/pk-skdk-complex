import { apiRequest } from '../../api/client.ts';
import { IS_DEMO_MODE } from '../../shared/config.ts';
import { parseDocumentCategories, type DocumentCategoryRead } from './documentCategoryContract.ts';

export type DocumentCategoriesRequest = (path: string) => Promise<unknown>;
export type DocumentCategoriesApiDependencies = {
  demoMode: boolean;
  request: DocumentCategoriesRequest;
  readDemoDocumentCategories: () => Promise<DocumentCategoryRead[]>;
};

const demoCategories: DocumentCategoryRead[] = [
  { id: 1, name: 'Policies', code: 'POLICY', description: 'Policy documents', is_active: true },
];

export async function getRealDocumentCategories(request: DocumentCategoriesRequest = apiRequest): Promise<DocumentCategoryRead[]> {
  return parseDocumentCategories(await request('/document-management/categories'));
}

export async function getDemoDocumentCategories(): Promise<DocumentCategoryRead[]> {
  return demoCategories.map((category) => ({ ...category }));
}

const defaults: DocumentCategoriesApiDependencies = {
  demoMode: IS_DEMO_MODE,
  request: apiRequest,
  readDemoDocumentCategories: getDemoDocumentCategories,
};

export function getDocumentCategories(dependencies: DocumentCategoriesApiDependencies = defaults): Promise<DocumentCategoryRead[]> {
  return dependencies.demoMode
    ? dependencies.readDemoDocumentCategories()
    : getRealDocumentCategories(dependencies.request);
}
