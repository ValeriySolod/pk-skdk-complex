export interface DocumentCategoryRead {
  id: number;
  name: string;
  code: string;
  description: string | null;
  is_active: boolean;
}

export class InvalidDocumentCategoriesResponseError extends Error {
  constructor() {
    super('The document categories response does not match the DocumentCategoryRead contract.');
    this.name = 'InvalidDocumentCategoriesResponseError';
  }
}

const contractKeys = ['code', 'description', 'id', 'is_active', 'name'];

function parseDocumentCategory(value: unknown): DocumentCategoryRead {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) throw new InvalidDocumentCategoriesResponseError();
  const category = value as Record<string, unknown>;
  const keys = Object.keys(category).sort();
  if (
    keys.length !== contractKeys.length ||
    keys.some((key, index) => key !== contractKeys[index]) ||
    !Number.isInteger(category.id) ||
    typeof category.name !== 'string' ||
    typeof category.code !== 'string' ||
    !(category.description === null || typeof category.description === 'string') ||
    typeof category.is_active !== 'boolean'
  ) throw new InvalidDocumentCategoriesResponseError();
  return category as unknown as DocumentCategoryRead;
}

export function parseDocumentCategories(value: unknown): DocumentCategoryRead[] {
  if (!Array.isArray(value)) throw new InvalidDocumentCategoriesResponseError();
  return value.map(parseDocumentCategory);
}
