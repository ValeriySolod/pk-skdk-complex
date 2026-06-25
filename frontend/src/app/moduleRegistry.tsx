import { OrganizationsPage } from '../modules/organizations/OrganizationsPage';
import { RegistriesPage } from '../modules/registries/RegistriesPage';
import { ShipmentsPage } from '../modules/shipments/ShipmentsPage';
import { ScannerPage } from '../modules/scanner/ScannerPage';
import { ReportsPage } from '../modules/reports/ReportsPage';
import { SearchPage } from '../modules/search/SearchPage';
import { AnalyticsPage } from '../modules/analytics/AnalyticsPage';
import { AdminPage } from '../modules/admin/AdminPage';
import { WorkflowPage } from '../modules/workflow/WorkflowPage';

export type FrontendModule = {
  code: string;
  title: string;
  path: string;
  Component: React.ComponentType;
};

export const modules: FrontendModule[] = [
  { code: 'organizations', title: 'Організації', path: '/organizations', Component: OrganizationsPage },
  { code: 'registries', title: 'Реєстри', path: '/registries', Component: RegistriesPage },
  { code: 'shipments', title: 'Відправлення', path: '/shipments', Component: ShipmentsPage },
  { code: 'scanner', title: 'Сканування', path: '/scanner', Component: ScannerPage },
  { code: 'search', title: 'Пошук', path: '/search', Component: SearchPage },
  { code: 'reports', title: 'Звіти', path: '/reports', Component: ReportsPage },
  { code: 'analytics', title: 'Аналітика', path: '/analytics', Component: AnalyticsPage },
  { code: 'workflow', title: 'Процес', path: '/workflow', Component: WorkflowPage },
  { code: 'admin', title: 'Адміністрування', path: '/admin', Component: AdminPage },
];
