import { useId, type KeyboardEvent, type ReactNode } from 'react';
import clsx from 'clsx';
import styles from './Tabs.module.css';

export interface TabItem {
  id: string;
  label: ReactNode;
  content: ReactNode;
  disabled?: boolean;
}

export interface TabsProps {
  items: TabItem[];
  activeId: string;
  onChange: (id: string) => void;
  variant?: 'line' | 'boxed';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  className?: string;
}

export function Tabs({
  items,
  activeId,
  onChange,
  variant = 'line',
  size = 'md',
  fullWidth = false,
  className,
}: TabsProps) {
  const generatedId = useId();
  const activeItem = items.find((item) => item.id === activeId);
  const activeIndex = items.findIndex((item) => item.id === activeId);
  const firstEnabledIndex = items.findIndex((item) => !item.disabled);
  const enabledItems = items.filter((item) => !item.disabled);

  if (items.length === 0) {
    return null;
  }

  const focusTab = (id: string) => {
    const tab = document.getElementById(getTabId(generatedId, id));
    tab?.focus();
  };

  const selectTab = (item: TabItem) => {
    if (!item.disabled && item.id !== activeId) {
      onChange(item.id);
    }
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (!enabledItems.length) {
      return;
    }

    const target = event.target instanceof HTMLElement ? event.target : null;
    const currentId = target?.getAttribute('data-tab-id') ?? activeId;
    const currentEnabledIndex = enabledItems.findIndex((item) => item.id === currentId);
    const safeCurrentIndex = currentEnabledIndex >= 0 ? currentEnabledIndex : 0;

    let nextItem: TabItem | undefined;

    switch (event.key) {
      case 'ArrowRight':
        event.preventDefault();
        nextItem = enabledItems[(safeCurrentIndex + 1) % enabledItems.length];
        break;
      case 'ArrowLeft':
        event.preventDefault();
        nextItem = enabledItems[(safeCurrentIndex - 1 + enabledItems.length) % enabledItems.length];
        break;
      case 'Home': {
        event.preventDefault();
        nextItem = enabledItems[0];
        break;
      }
      case 'End': {
        event.preventDefault();
        nextItem = enabledItems[enabledItems.length - 1];
        break;
      }
      default:
        return;
    }

    if (nextItem) {
      onChange(nextItem.id);
      requestAnimationFrame(() => focusTab(nextItem.id));
    }
  };

  return (
    <div className={clsx(styles.root, className)}>
      <div
        className={clsx(
          styles.tabs,
          styles[variant],
          styles[size],
          fullWidth && styles.fullWidth,
        )}
        role="tablist"
        onKeyDown={handleKeyDown}
      >
        {items.map((item, index) => {
          const selected = item.id === activeId;
          const isFallbackFocusable = activeIndex === -1 && index === firstEnabledIndex;
          const tabIndex = selected || isFallbackFocusable ? 0 : -1;

          return (
            <button
              id={getTabId(generatedId, item.id)}
              className={clsx(styles.tab, selected && styles.active)}
              type="button"
              role="tab"
              aria-selected={selected}
              aria-controls={getPanelId(generatedId, item.id)}
              disabled={item.disabled}
              tabIndex={item.disabled ? -1 : tabIndex}
              key={item.id}
              data-tab-id={item.id}
              onClick={() => selectTab(item)}
            >
              {item.label}
            </button>
          );
        })}
      </div>

      {activeItem && (
        <div
          id={getPanelId(generatedId, activeItem.id)}
          className={styles.panel}
          role="tabpanel"
          aria-labelledby={getTabId(generatedId, activeItem.id)}
          tabIndex={0}
        >
          {activeItem.content}
        </div>
      )}
    </div>
  );
}

function getTabId(baseId: string, tabId: string) {
  return `${baseId}-${tabId}-tab`;
}

function getPanelId(baseId: string, tabId: string) {
  return `${baseId}-${tabId}-panel`;
}
