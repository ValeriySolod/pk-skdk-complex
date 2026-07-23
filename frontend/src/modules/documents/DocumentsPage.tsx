import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Button, EmptyState, Loader, PageHeader, Table, type TableColumn } from '../../shared/ui';
import type { DocumentRead } from './documentContract.ts';
import type { DocumentVersionRead } from './documentVersionContract.ts';
import { createDocumentsPageCoordinator, type DocumentsPageCoordinator } from './documentsPageCoordinator.ts';
import { documentsErrorMessages, type DocumentsState } from './documentsState.ts';
import { createDocumentVersionsPageCoordinator, type DocumentVersionsPageCoordinator } from './documentVersionsPageCoordinator.ts';
import { documentVersionsErrorMessages, type DocumentVersionsState } from './documentVersionsState.ts';
import styles from './DocumentsPage.module.css';
export function DocumentsPage() {
  const [state, setState] = useState<DocumentsState>({ status: 'loading' }); const coordinator = useRef<DocumentsPageCoordinator | null>(null);
  const [versionsState, setVersionsState] = useState<DocumentVersionsState>({ status: 'unselected' });
  if (coordinator.current === null) coordinator.current = createDocumentsPageCoordinator({ applyState: setState, navigateToLogin: () => window.location.assign('/login') });
  const versionsCoordinator = useRef<DocumentVersionsPageCoordinator | null>(null);
  if (versionsCoordinator.current === null) versionsCoordinator.current = createDocumentVersionsPageCoordinator({ applyState: setVersionsState, navigateToLogin: () => window.location.assign('/login') });
  const load = useCallback(async () => { await coordinator.current?.load(); }, []);
  const selectDocument = useCallback(async (document: DocumentRead) => { await versionsCoordinator.current?.load(document.id); }, []);
  const retryVersions = useCallback(async () => {
    if ('documentId' in versionsState) await versionsCoordinator.current?.load(versionsState.documentId);
  }, [versionsState]);
  useEffect(() => { void load(); return () => { coordinator.current?.invalidate(); versionsCoordinator.current?.invalidate(); }; }, [load]);
  const columns = useMemo<readonly TableColumn<DocumentRead>[]>(() => [
    { id: 'number', header: 'Document number', cell: (item) => item.document_number ?? '—' }, { id: 'title', header: 'Title', cell: (item) => item.title },
    { id: 'type', header: 'Type', cell: (item) => item.document_type }, { id: 'status', header: 'Status', cell: (item) => item.status },
    { id: 'organization', header: 'Organization ID', cell: (item) => item.organization_id ?? '—' }, { id: 'owner', header: 'Owner user ID', cell: (item) => item.owner_user_id ?? '—' },
    { id: 'updated', header: 'Updated', cell: (item) => item.updated_at },
  ], []);
  const versionColumns = useMemo<readonly TableColumn<DocumentVersionRead>[]>(() => [
    { id: 'version', header: 'Version', cell: (item) => item.version },
    { id: 'fileName', header: 'File name', cell: (item) => item.file_name },
    { id: 'storagePath', header: 'Storage path', cell: (item) => item.storage_path },
    { id: 'checksum', header: 'Checksum', cell: (item) => item.checksum ?? '—' },
    { id: 'uploadedBy', header: 'Uploaded by', cell: (item) => item.uploaded_by ?? '—' },
    { id: 'uploadedAt', header: 'Uploaded at', cell: (item) => item.uploaded_at },
  ], []);
  return <div className={styles.page}><PageHeader title="Document management" description="Read-only documents from the backend" />
    {state.status === 'loading' && <div className={styles.status} role="status" aria-live="polite"><Loader /><span>Loading documents...</span></div>}
    {state.status === 'error' && <div className={styles.errorPanel} role="alert"><p>{documentsErrorMessages[state.failure]}</p><Button type="button" onClick={() => void load()}>Retry</Button></div>}
    {state.status === 'success' && state.documents.length === 0 && <EmptyState title="No documents found" />}
    {state.status === 'success' && state.documents.length > 0 && <Table columns={columns} data={state.documents} getRowKey={(item) => item.id} caption="Documents" onRowClick={(document) => void selectDocument(document)} rowClassName={(document) => ('documentId' in versionsState && versionsState.documentId === document.id ? styles.selectedRow : undefined)} />}
    <section className={styles.section} aria-labelledby="document-versions-heading">
      <h2 id="document-versions-heading">Document versions</h2>
      {versionsState.status === 'unselected' && <EmptyState title="Select a document to view versions" />}
      {versionsState.status === 'loading' && <div className={styles.status} role="status" aria-live="polite"><Loader /><span>Loading document versions...</span></div>}
      {versionsState.status === 'error' && <div className={styles.errorPanel} role="alert"><p>{documentVersionsErrorMessages[versionsState.failure]}</p><Button type="button" onClick={() => void retryVersions()}>Retry document versions</Button></div>}
      {versionsState.status === 'success' && versionsState.versions.length === 0 && <EmptyState title="No document versions found" />}
      {versionsState.status === 'success' && versionsState.versions.length > 0 && <Table columns={versionColumns} data={versionsState.versions} getRowKey={(item) => item.id} caption={`Versions for document ${versionsState.documentId}`} />}
    </section>
  </div>;
}
