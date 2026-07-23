import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Button, EmptyState, Loader, PageHeader, Table, type TableColumn } from '../../shared/ui';
import type { DocumentRead } from './documentContract.ts';
import { createDocumentsPageCoordinator, type DocumentsPageCoordinator } from './documentsPageCoordinator.ts';
import { documentsErrorMessages, type DocumentsState } from './documentsState.ts';
import styles from './DocumentsPage.module.css';
export function DocumentsPage() {
  const [state, setState] = useState<DocumentsState>({ status: 'loading' }); const coordinator = useRef<DocumentsPageCoordinator | null>(null);
  if (coordinator.current === null) coordinator.current = createDocumentsPageCoordinator({ applyState: setState, navigateToLogin: () => window.location.assign('/login') });
  const load = useCallback(async () => { await coordinator.current?.load(); }, []);
  useEffect(() => { void load(); return () => coordinator.current?.invalidate(); }, [load]);
  const columns = useMemo<readonly TableColumn<DocumentRead>[]>(() => [
    { id: 'number', header: 'Document number', cell: (item) => item.document_number ?? '—' }, { id: 'title', header: 'Title', cell: (item) => item.title },
    { id: 'type', header: 'Type', cell: (item) => item.document_type }, { id: 'status', header: 'Status', cell: (item) => item.status },
    { id: 'organization', header: 'Organization ID', cell: (item) => item.organization_id ?? '—' }, { id: 'owner', header: 'Owner user ID', cell: (item) => item.owner_user_id ?? '—' },
    { id: 'updated', header: 'Updated', cell: (item) => item.updated_at },
  ], []);
  return <div className={styles.page}><PageHeader title="Document management" description="Read-only documents from the backend" />
    {state.status === 'loading' && <div className={styles.status} role="status" aria-live="polite"><Loader /><span>Loading documents...</span></div>}
    {state.status === 'error' && <div className={styles.errorPanel} role="alert"><p>{documentsErrorMessages[state.failure]}</p><Button type="button" onClick={() => void load()}>Retry</Button></div>}
    {state.status === 'success' && state.documents.length === 0 && <EmptyState title="No documents found" />}
    {state.status === 'success' && state.documents.length > 0 && <Table columns={columns} data={state.documents} getRowKey={(item) => item.id} caption="Documents" />}
  </div>;
}
