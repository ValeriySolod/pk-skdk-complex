import type { Key, ReactNode } from 'react';
import clsx from 'clsx';

import styles from './DataGrid.module.css';

export type DataGridAlign = 'left' | 'center' | 'right';

export interface DataGridColumn<T extends object> {
  key: keyof T | string;
  header: ReactNode;
  render?: (row: T) => ReactNode;
  align?: DataGridAlign;
  width?: string | number;
}

export interface DataGridProps<T extends object> {
  columns: DataGridColumn<T>[];
  rows: T[];
  rowKey: (row: T) => Key;
  emptyMessage?: ReactNode;
  striped?: boolean;
  hoverable?: boolean;
  compact?: boolean;
  className?: string;
}

function getCellContent<T extends object>(row: T, column: DataGridColumn<T>): ReactNode {
  if (column.render) {
    return column.render(row);
  }

  if (typeof column.key === 'string' && !Object.prototype.hasOwnProperty.call(row, column.key)) {
    return null;
  }

  const value = row[column.key as keyof T];

  if (value === null || value === undefined) {
    return null;
  }

  if (
    typeof value === 'string' ||
    typeof value === 'number' ||
    typeof value === 'boolean' ||
    typeof value === 'bigint'
  ) {
    return String(value);
  }

  return null;
}

export function DataGrid<T extends object>({
  columns,
  rows,
  rowKey,
  emptyMessage = 'No data',
  striped = false,
  hoverable = false,
  compact = false,
  className,
}: DataGridProps<T>) {
  const hasRows = rows.length > 0;

  return (
    <div className={clsx(styles.wrapper, className)}>
      <table
        className={clsx(
          styles.table,
          striped && styles.striped,
          hoverable && styles.hoverable,
          compact && styles.compact,
        )}
      >
        <thead className={styles.head}>
          <tr>
            {columns.map((column) => (
              <th
                className={clsx(styles.headerCell, styles[column.align ?? 'left'])}
                key={String(column.key)}
                scope="col"
                style={{ width: column.width }}
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>

        <tbody className={styles.body}>
          {hasRows ? (
            rows.map((row) => (
              <tr className={styles.row} key={rowKey(row)}>
                {columns.map((column) => (
                  <td className={clsx(styles.cell, styles[column.align ?? 'left'])} key={String(column.key)}>
                    {getCellContent(row, column)}
                  </td>
                ))}
              </tr>
            ))
          ) : (
            <tr>
              <td className={styles.emptyCell} colSpan={Math.max(columns.length, 1)}>
                {emptyMessage}
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
