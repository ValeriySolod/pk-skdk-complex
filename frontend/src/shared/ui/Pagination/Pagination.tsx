import type { ButtonHTMLAttributes } from 'react';
import clsx from 'clsx';
import styles from './Pagination.module.css';

export interface PaginationProps {
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  className?: string;
  disabled?: boolean;
  siblingCount?: number;
  boundaryCount?: number;
  ariaLabel?: string;
  previousLabel?: string;
  nextLabel?: string;
}

type PaginationItem = number | 'ellipsis';

export function Pagination({
  page,
  totalPages,
  onPageChange,
  className,
  disabled = false,
  siblingCount = 1,
  boundaryCount = 1,
  ariaLabel = 'Навігація сторінками',
  previousLabel = 'Попередня',
  nextLabel = 'Наступна',
}: PaginationProps) {
  const safeTotalPages = Math.max(1, totalPages);
  const currentPage = clamp(page, 1, safeTotalPages);
  const items = getPaginationItems(currentPage, safeTotalPages, siblingCount, boundaryCount);
  const isPreviousDisabled = disabled || currentPage <= 1;
  const isNextDisabled = disabled || currentPage >= safeTotalPages;

  const changePage = (nextPage: number) => {
    const safeNextPage = clamp(nextPage, 1, safeTotalPages);

    if (!disabled && safeNextPage !== currentPage) {
      onPageChange(safeNextPage);
    }
  };

  return (
    <nav className={clsx(styles.pagination, className)} aria-label={ariaLabel}>
      <ul className={styles.list}>
        <li>
          <PaginationButton disabled={isPreviousDisabled} onClick={() => changePage(currentPage - 1)}>
            {previousLabel}
          </PaginationButton>
        </li>

        {items.map((item, index) => {
          if (item === 'ellipsis') {
            return (
              <li aria-hidden="true" key={`ellipsis-${index}`}>
                <span className={styles.ellipsis}>…</span>
              </li>
            );
          }

          const isCurrent = item === currentPage;

          return (
            <li key={item}>
              <PaginationButton
                aria-current={isCurrent ? 'page' : undefined}
                className={clsx(isCurrent && styles.active)}
                disabled={disabled || isCurrent}
                onClick={() => changePage(item)}
              >
                <span className={styles.visuallyHidden}>Сторінка </span>
                {item}
              </PaginationButton>
            </li>
          );
        })}

        <li>
          <PaginationButton disabled={isNextDisabled} onClick={() => changePage(currentPage + 1)}>
            {nextLabel}
          </PaginationButton>
        </li>
      </ul>
    </nav>
  );
}

function PaginationButton({ className, type = 'button', ...props }: ButtonHTMLAttributes<HTMLButtonElement>) {
  return <button className={clsx(styles.button, className)} type={type} {...props} />;
}

export function getPaginationItems(
  currentPage: number,
  totalPages: number,
  siblingCount = 1,
  boundaryCount = 1,
): PaginationItem[] {
  const safeTotalPages = Math.max(1, totalPages);
  const safeCurrentPage = clamp(currentPage, 1, safeTotalPages);
  const safeSiblingCount = Math.max(0, siblingCount);
  const safeBoundaryCount = Math.max(0, boundaryCount);
  const totalVisibleNumbers = safeBoundaryCount * 2 + safeSiblingCount * 2 + 3;

  if (safeTotalPages <= totalVisibleNumbers) {
    return range(1, safeTotalPages);
  }

  const startPages = range(1, Math.min(safeBoundaryCount, safeTotalPages));
  const endPages = range(Math.max(safeTotalPages - safeBoundaryCount + 1, safeBoundaryCount + 1), safeTotalPages);

  const siblingsStart = Math.max(
    Math.min(
      safeCurrentPage - safeSiblingCount,
      safeTotalPages - safeBoundaryCount - safeSiblingCount * 2 - 1,
    ),
    safeBoundaryCount + 2,
  );

  const siblingsEnd = Math.min(
    Math.max(safeCurrentPage + safeSiblingCount, safeBoundaryCount + safeSiblingCount * 2 + 2),
    endPages.length > 0 ? endPages[0] - 2 : safeTotalPages - 1,
  );

  const items: PaginationItem[] = [...startPages];

  if (siblingsStart > safeBoundaryCount + 2) {
    items.push('ellipsis');
  } else {
    const nextPage = safeBoundaryCount + 1;
    if (nextPage < siblingsStart) {
      items.push(nextPage);
    }
  }

  items.push(...range(siblingsStart, siblingsEnd));

  if (siblingsEnd < safeTotalPages - safeBoundaryCount - 1) {
    items.push('ellipsis');
  } else {
    const previousPage = safeTotalPages - safeBoundaryCount;
    if (previousPage > siblingsEnd) {
      items.push(previousPage);
    }
  }

  items.push(...endPages);

  return items;
}

function range(start: number, end: number) {
  if (end < start) {
    return [];
  }

  return Array.from({ length: end - start + 1 }, (_, index) => start + index);
}

function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max);
}
