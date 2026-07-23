import { lazy, type ComponentType, type LazyExoticComponent } from 'react';

const OrganizationsPage = lazy(() =>
  import('../modules/organizations/OrganizationsPage').then(({ OrganizationsPage }) => ({
    default: OrganizationsPage,
  })),
);
const RegistriesPage = lazy(() =>
  import('../modules/registries/RegistriesPage').then(({ RegistriesPage }) => ({
    default: RegistriesPage,
  })),
);
const IncomingRegistryPage = lazy(() =>
  import('../modules/registries/pages/IncomingRegistryPage').then(({ IncomingRegistryPage }) => ({
    default: IncomingRegistryPage,
  })),
);
const ShipmentsPage = lazy(() =>
  import('../modules/shipments/ShipmentsPage').then(({ ShipmentsPage }) => ({
    default: ShipmentsPage,
  })),
);
const ScannerPage = lazy(() =>
  import('../modules/scanner/ScannerPage').then(({ ScannerPage }) => ({
    default: ScannerPage,
  })),
);
const ReportsPage = lazy(() =>
  import('../modules/reports/ReportsPage').then(({ ReportsPage }) => ({
    default: ReportsPage,
  })),
);
const SearchPage = lazy(() =>
  import('../modules/search/SearchPage').then(({ SearchPage }) => ({
    default: SearchPage,
  })),
);
const AnalyticsPage = lazy(() =>
  import('../modules/analytics/AnalyticsPage').then(({ AnalyticsPage }) => ({
    default: AnalyticsPage,
  })),
);
const AdminPage = lazy(() =>
  import('../modules/admin/AdminPage').then(({ AdminPage }) => ({
    default: AdminPage,
  })),
);
const WorkflowPage = lazy(() =>
  import('../modules/workflow/WorkflowPage').then(({ WorkflowPage }) => ({
    default: WorkflowPage,
  })),
);
const DocumentsPage = lazy(() =>
  import('../modules/documents/DocumentsPage').then(({ DocumentsPage }) => ({ default: DocumentsPage })),
);

export type ModuleNavigation = {
  order: number;
  group?: string;
};

export type ModuleDefinition = {
  id: string;
  title: string;
  path: string;
  Component: LazyExoticComponent<ComponentType>;
  icon?: string;
  roles?: readonly string[];
  navigation?: ModuleNavigation;
};

export type NavigableModuleDefinition = ModuleDefinition & {
  navigation: ModuleNavigation;
};

export function hasModuleNavigation(module: ModuleDefinition): module is NavigableModuleDefinition {
  return module.navigation !== undefined;
}

export function isModuleVisibleForRole(module: ModuleDefinition, role: string): boolean {
  return module.roles === undefined || module.roles.includes(role);
}

export const modules: ModuleDefinition[] = [
  {
    id: 'organizations',
    title: 'Організації',
    path: '/organizations',
    Component: OrganizationsPage,
    navigation: { order: 10 },
  },
  {
    id: 'registries',
    title: 'Реєстри',
    path: '/registries',
    Component: RegistriesPage,
    navigation: { order: 20 },
  },
  {
    id: 'registries-incoming',
    title: 'Вхідний реєстр',
    path: '/registries/incoming',
    Component: IncomingRegistryPage,
  },
  {
    id: 'documents',
    title: 'Documents',
    path: '/documents',
    Component: DocumentsPage,
    navigation: { order: 25 },
  },
  {
    id: 'shipments',
    title: 'Відправлення',
    path: '/shipments',
    Component: ShipmentsPage,
    navigation: { order: 30 },
  },
  {
    id: 'scanner',
    title: 'Сканування',
    path: '/scanner',
    Component: ScannerPage,
    navigation: { order: 40 },
  },
  {
    id: 'search',
    title: 'Пошук',
    path: '/search',
    Component: SearchPage,
    navigation: { order: 50 },
  },
  {
    id: 'reports',
    title: 'Звіти',
    path: '/reports',
    Component: ReportsPage,
    navigation: { order: 60 },
  },
  {
    id: 'analytics',
    title: 'Аналітика',
    path: '/analytics',
    Component: AnalyticsPage,
    navigation: { order: 70 },
  },
  {
    id: 'workflow',
    title: 'Процес',
    path: '/workflow',
    Component: WorkflowPage,
    navigation: { order: 80 },
  },
  {
    id: 'admin',
    title: 'Адміністрування',
    path: '/admin',
    Component: AdminPage,
    roles: ['SYSTEM_ADMIN'],
    navigation: { order: 90 },
  },
];
