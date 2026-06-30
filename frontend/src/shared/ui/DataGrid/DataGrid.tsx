import type { ReactNode } from 'react';
import clsx from 'clsx';

import styles from './DataGrid.module.css';

export interface DataGridColumn<TItem> {
  key: string;
  header: ReactNode;
  render: (item: TItem, index: number) => ReactNode;
  align?: 'left' | 'center' | 'right';
  width?: string;
}

export interface DataGridProps<TItem> {
  items: TItem[];
  columns: DataGridColumn<TItem>[];
  getRowKey: (item: TItem, index: number) => string | number;
  caption?: string;
  emptyMessage?: ReactNode;
  loading?: boolean;
  striped?: boolean;
  bordered?: boolean;
  compact?: boolean;
  className?: string;
}

export function DataGrid<TItem>({
  items,
  columns,
  getRowKey,
  caption,
  emptyMessage = 'No data to display',
  loading = false,
  striped = false,
  bordered = false,
  compact = false,
  className,
}: DataGridProps<TItem>) {
  if (columns.length === 0) {
    return null;
  }

  const stateMessage = loading ? 'Loading data...' : emptyMessage;
  const shouldShowState = loading || items.length === 0;

  return (
    <div className={clsx(styles.wrapper, className)} aria-busy={loading ? true : undefined}>
      <table
        className={clsx(
          styles.table,
          striped && styles.striped,
          bordered && styles.bordered,
          compact && styles.compact,
        )}
      >
        {caption ? <caption className={styles.caption}>{caption}</caption> : null}

        <thead className={styles.head}>
          <tr>
            {columns.map((column) => (
              <th
                className={clsx(styles.headerCell, styles[column.align ?? 'left'])}
                key={column.key}
                scope="col"
                style={column.width ? { width: column.width } : undefined}
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>

        <tbody className={styles.body}>
          {shouldShowState ? (
            <tr>
              <td className={styles.stateCell} colSpan={columns.length}>
                {loading ? (
                  <span role="status" aria-live="polite">
                    {stateMessage}
                  </span>
                ) : (
                  stateMessage
                )}
              </td>
            </tr>
          ) : (
            items.map((item, index) => (
              <tr className={styles.row} key={getRowKey(item, index)}>
                {columns.map((column) => (
                  <td className={clsx(styles.cell, styles[column.align ?? 'left'])} key={column.key}>
                    {column.render(item, index)}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
