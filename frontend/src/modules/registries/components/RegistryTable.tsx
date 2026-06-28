import { StatusBadge } from '../../../shared/components';
import type { RegistryRecord } from '../types';
import css from '../RegistriesPage.module.css';

interface RegistryTableProps {
  items: RegistryRecord[];
}

export function RegistryTable({ items }: RegistryTableProps) {
  if (items.length === 0) {
    return <p className={css.empty}>Записів поки немає.</p>;
  }

  return (
    <div className={css.tableWrap}>
      <table className={css.table}>
        <thead>
          <tr>
            <th>№</th>
            <th>Дата</th>
            <th>Організація</th>
            <th>QR</th>
            <th>Статус</th>
          </tr>
        </thead>

        <tbody>
          {items.map((item) => (
            <tr key={item.id}>
              <td>{item.number}</td>
              <td>{new Date(item.received_at).toLocaleString('uk-UA')}</td>
              <td>ID: {item.sender_org_id}</td>
              <td>{item.qr_payload || '—'}</td>
              <td>
                <StatusBadge status={item.status} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}