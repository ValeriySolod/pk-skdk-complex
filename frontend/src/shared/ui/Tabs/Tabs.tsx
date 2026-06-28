import { useId, type KeyboardEvent, type ReactNode } from 'react';
import clsx from 'clsx';
import styles from './Tabs.module.css';

export interface TabItem {
  id: string;
  label: ReactNode;
  disabled?: boolean;
}

export interface TabsProps {
  items: TabItem[];
  value: string;
  onChange: (id: string) => void;
  className?: string;
  variant?: 'line' | 'contained';
  size?: 'sm' | 'md';
  fullWidth?: boolean;
}

export function Tabs({
  items,
  value,
  onChange,
  className,
  variant = 'line',
  size = 'md',
  fullWidth = false,
}: TabsProps) {
  const generatedId = useId();
  const activeIndex = items.findIndex((item) => item.id === value);

  const enabledItems = items.filter((item) => !item.disabled);

  const focusTab = (id: string) => {
    const tab = document.getElementById(getTabId(generatedId, id));
    tab?.focus();
  };

  const selectTab = (item: TabItem) => {
    if (!item.disabled && item.id !== value) {
      onChange(item.id);
    }
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (!enabledItems.length) {
      return;
    }

    const currentEnabledIndex = enabledItems.findIndex((item) => item.id === value);
    const safeCurrentIndex = currentEnabledIndex >= 0 ? currentEnabledIndex : 0;

    let nextItem: TabItem | undefined;

    switch (event.key) {
      case 'ArrowRight':
      case 'ArrowDown': {
        event.preventDefault();
        nextItem = enabledItems[(safeCurrentIndex + 1) % enabledItems.length];
        break;
      }
      case 'ArrowLeft':
      case 'ArrowUp': {
        event.preventDefault();
        nextItem = enabledItems[(safeCurrentIndex - 1 + enabledItems.length) % enabledItems.length];
        break;
      }
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
    <div
      className={clsx(
        styles.tabs,
        styles[variant],
        styles[size],
        fullWidth && styles.fullWidth,
        className,
      )}
      role="tablist"
      onKeyDown={handleKeyDown}
    >
      {items.map((item, index) => {
        const selected = item.id === value;
        const tabIndex = selected || (activeIndex === -1 && index === 0) ? 0 : -1;

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
            onClick={() => selectTab(item)}
          >
            {item.label}
          </button>
        );
      })}
    </div>
  );
}

export function getTabId(baseId: string, tabId: string) {
  return `${baseId}-${tabId}-tab`;
}

export function getPanelId(baseId: string, tabId: string) {
  return `${baseId}-${tabId}-panel`;
}
