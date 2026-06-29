import type { ReactNode } from 'react';
import { useId, useState } from 'react';
import clsx from 'clsx';
import styles from './Accordion.module.css';

export interface AccordionItem {
  id: string;
  title: ReactNode;
  children: ReactNode;
  disabled?: boolean;
}

export interface AccordionProps {
  items: AccordionItem[];
  allowMultiple?: boolean;
  defaultOpenIds?: string[];
  openIds?: string[];
  onOpenChange?: (openIds: string[]) => void;
  className?: string;
}

function isRenderableContent(content: ReactNode) {
  return content !== undefined && content !== null && content !== false && content !== '';
}

function normalizeOpenIds(openIds: string[] | undefined, itemIds: Set<string>) {
  if (!openIds) {
    return [];
  }

  return openIds.filter((id, index) => itemIds.has(id) && openIds.indexOf(id) === index);
}

export function Accordion({
  items,
  allowMultiple = false,
  defaultOpenIds,
  openIds,
  onOpenChange,
  className,
}: AccordionProps) {
  const baseId = useId();
  const itemIds = new Set(items.map((item) => item.id));
  const [internalOpenIds, setInternalOpenIds] = useState(() =>
    normalizeOpenIds(defaultOpenIds, itemIds),
  );

  if (items.length === 0) {
    return null;
  }

  const isControlled = openIds !== undefined;
  const currentOpenIds = normalizeOpenIds(
    isControlled ? openIds : internalOpenIds,
    itemIds,
  );

  function updateOpenIds(nextOpenIds: string[]) {
    if (!isControlled) {
      setInternalOpenIds(nextOpenIds);
    }

    onOpenChange?.(nextOpenIds);
  }

  function handleToggle(itemId: string) {
    const isOpen = currentOpenIds.includes(itemId);
    const nextOpenIds = isOpen
      ? currentOpenIds.filter((id) => id !== itemId)
      : allowMultiple
        ? [...currentOpenIds, itemId]
        : [itemId];

    updateOpenIds(nextOpenIds);
  }

  return (
    <div className={clsx(styles.accordion, className)}>
      {items.map((item) => {
        const isOpen = currentOpenIds.includes(item.id);
        const buttonId = `${baseId}-${item.id}-button`;
        const panelId = `${baseId}-${item.id}-panel`;
        const hasContent = isRenderableContent(item.children);

        return (
          <section className={styles.item} key={item.id}>
            <h3 className={styles.heading}>
              <button
                className={styles.trigger}
                type="button"
                id={buttonId}
                aria-expanded={isOpen}
                aria-controls={panelId}
                disabled={item.disabled}
                onClick={() => handleToggle(item.id)}
              >
                <span className={styles.title}>{item.title}</span>
                <span className={styles.icon} aria-hidden="true">
                  {isOpen ? '−' : '+'}
                </span>
              </button>
            </h3>

            <div
              className={clsx(styles.panel, isOpen && styles.open)}
              id={panelId}
              role="region"
              aria-labelledby={buttonId}
              hidden={!isOpen}
            >
              {hasContent && <div className={styles.content}>{item.children}</div>}
            </div>
          </section>
        );
      })}
    </div>
  );
}
