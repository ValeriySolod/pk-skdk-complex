import type { KeyboardEvent, ReactNode, TableHTMLAttributes } from 'react';
import clsx from 'clsx';
import styles from './Table.module.css';

export type TableSize = 'sm' | 'md';
export type TableAlign = 'left' | 'center' | 'right';

export interface TableColumn<TData extends object> {
  id: string;
  header: ReactNode;
  cell: (row: TData, index: number) => ReactNode;
  align?: TableAlign;
  width?: string | number;
  className?: string;
  headerClassName?: string;
}

export interface TableProps<TData extends object> extends Omit<TableHTMLAttributes<HTMLTableElement>, 'children'> {
  columns: readonly TableColumn<TData>[];
  data: readonly TData[];
  getRowKey?: (row: TData, index: number) => string | number;
  caption?: ReactNode;
  emptyMessage?: ReactNode;
  loadingMessage?: ReactNode;
  isLoading?: boolean;
  size?: TableSize;
  striped?: boolean;
  bordered?: boolean;
  stickyHeader?: boolean;
  wrapperClassName?: string;
  rowClassName?: (row: TData, index: number) => string | undefined;
  onRowClick?: (row: TData, index: number) => void;
}

export function Table<TData extends object>({
  columns,
  data,
  getRowKey,
  caption,
  emptyMessage = 'Немає даних для відображення',
  loadingMessage = 'Завантаження даних...',
  isLoading = false,
  size = 'md',
  striped = false,
  bordered = false,
  stickyHeader = false,
  wrapperClassName,
  rowClassName,
  onRowClick,
  className,
  ...props
}: TableProps<TData>) {
  const hasInteractiveRows = Boolean(onRowClick);
  const shouldShowState = isLoading || data.length === 0;

  const handleRowKeyDown = (event: KeyboardEvent<HTMLTableRowElement>, row: TData, index: number) => {
    if (!onRowClick) {
      return;
    }

    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      onRowClick(row, index);
    }
  };

  return (
    <div className={clsx(styles.wrapper, wrapperClassName)}>
      <table
        className={clsx(
          styles.table,
          styles[size],
          striped && styles.striped,
          bordered && styles.bordered,
          stickyHeader && styles.stickyHeader,
          hasInteractiveRows && styles.interactiveRows,
          className,
        )}
        {...props}
      >
        {caption && <caption className={styles.caption}>{caption}</caption>}

        <thead className={styles.head}>
          <tr>
            {columns.map((column) => (
              <th
                className={clsx(styles.headerCell, styles[column.align ?? 'left'], column.headerClassName)}
                key={column.id}
                scope="col"
                style={{ width: column.width }}
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>

        <tbody className={styles.body}>
          {shouldShowState ? (
            <tr>
              <td className={styles.stateCell} colSpan={Math.max(columns.length, 1)}>
                {isLoading ? loadingMessage : emptyMessage}
              </td>
            </tr>
          ) : (
            data.map((row, index) => {
              const key = getRowKey ? getRowKey(row, index) : index;

              return (
                <tr
                  className={clsx(styles.row, rowClassName?.(row, index))}
                  key={key}
                  tabIndex={hasInteractiveRows ? 0 : undefined}
                  onClick={onRowClick ? () => onRowClick(row, index) : undefined}
                  onKeyDown={hasInteractiveRows ? (event) => handleRowKeyDown(event, row, index) : undefined}
                >
                  {columns.map((column) => (
                    <td className={clsx(styles.cell, styles[column.align ?? 'left'], column.className)} key={column.id}>
                      {column.cell(row, index)}
                    </td>
                  ))}
                </tr>
              );
            })
          )}
        </tbody>
      </table>
    </div>
  );
}
