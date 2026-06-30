import { useEffect, useRef, useState, type KeyboardEvent, type ReactNode } from 'react';
import clsx from 'clsx';
import styles from './Menu.module.css';

export interface MenuItem {
  id: string;
  label: ReactNode;
  icon?: ReactNode;
  disabled?: boolean;
  danger?: boolean;
  onSelect?: () => void;
}

export interface MenuProps {
  items: MenuItem[];
  orientation?: 'vertical' | 'horizontal';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function Menu({
  items,
  orientation = 'vertical',
  size = 'md',
  className,
}: MenuProps) {
  const itemRefs = useRef<Array<HTMLButtonElement | null>>([]);
  const [activeIndex, setActiveIndex] = useState(() => getFirstEnabledIndex(items));
  const focusableIndex = isEnabledItem(items, activeIndex)
    ? activeIndex
    : getFirstEnabledIndex(items);

  useEffect(() => {
    if (!isEnabledItem(items, activeIndex)) {
      setActiveIndex(getFirstEnabledIndex(items));
    }
  }, [activeIndex, items]);

  if (items.length === 0) {
    return null;
  }

  function focusItem(index: number) {
    setActiveIndex(index);
    requestAnimationFrame(() => {
      itemRefs.current[index]?.focus();
    });
  }

  function getNextEnabledIndex(currentIndex: number, direction: 1 | -1) {
    if (items.every((item) => item.disabled)) {
      return -1;
    }

    let nextIndex = currentIndex;

    for (let step = 0; step < items.length; step += 1) {
      nextIndex = (nextIndex + direction + items.length) % items.length;

      if (!items[nextIndex]?.disabled) {
        return nextIndex;
      }
    }

    return -1;
  }

  function handleKeyDown(event: KeyboardEvent<HTMLUListElement>) {
    const target = event.target instanceof HTMLButtonElement ? event.target : null;
    const currentIndex = Number(target?.dataset.menuIndex ?? focusableIndex);
    const safeCurrentIndex = Number.isNaN(currentIndex) ? focusableIndex : currentIndex;

    switch (event.key) {
      case 'ArrowDown':
      case 'ArrowRight': {
        event.preventDefault();
        const nextIndex = getNextEnabledIndex(safeCurrentIndex, 1);

        if (nextIndex >= 0) {
          focusItem(nextIndex);
        }
        break;
      }
      case 'ArrowUp':
      case 'ArrowLeft': {
        event.preventDefault();
        const nextIndex = getNextEnabledIndex(safeCurrentIndex, -1);

        if (nextIndex >= 0) {
          focusItem(nextIndex);
        }
        break;
      }
      case 'Home': {
        event.preventDefault();

        if (focusableIndex >= 0) {
          focusItem(getFirstEnabledIndex(items));
        }
        break;
      }
      case 'End': {
        event.preventDefault();
        const lastEnabledIndex = getLastEnabledIndex(items);

        if (lastEnabledIndex >= 0) {
          focusItem(lastEnabledIndex);
        }
        break;
      }
      case 'Enter':
      case ' ': {
        const item = items[safeCurrentIndex];

        if (item && !item.disabled) {
          event.preventDefault();
          item.onSelect?.();
        }
        break;
      }
      default:
        break;
    }
  }

  function handleSelect(item: MenuItem) {
    if (item.disabled) {
      return;
    }

    item.onSelect?.();
  }

  return (
    <nav className={clsx(styles.nav, className)} aria-label="Menu">
      <ul
        className={clsx(styles.menu, styles[orientation], styles[size])}
        role="menu"
        aria-orientation={orientation}
        onKeyDown={handleKeyDown}
      >
        {items.map((item, index) => (
          <li className={styles.menuItem} role="none" key={item.id}>
            <button
              ref={(element) => {
                itemRefs.current[index] = element;
              }}
              className={clsx(
                styles.item,
                index === activeIndex && styles.active,
                item.danger && styles.danger,
              )}
              type="button"
              role="menuitem"
              aria-disabled={item.disabled}
              disabled={item.disabled}
              tabIndex={index === focusableIndex && !item.disabled ? 0 : -1}
              data-menu-index={index}
              onClick={() => handleSelect(item)}
              onFocus={() => setActiveIndex(index)}
              onMouseEnter={() => {
                if (!item.disabled) {
                  setActiveIndex(index);
                }
              }}
            >
              {item.icon && (
                <span className={styles.icon} aria-hidden="true">
                  {item.icon}
                </span>
              )}
              <span className={styles.label}>{item.label}</span>
            </button>
          </li>
        ))}
      </ul>
    </nav>
  );
}

function isEnabledItem(items: MenuItem[], index: number) {
  return index >= 0 && index < items.length && !items[index]?.disabled;
}

function getFirstEnabledIndex(items: MenuItem[]) {
  return items.findIndex((item) => !item.disabled);
}

function getLastEnabledIndex(items: MenuItem[]) {
  for (let index = items.length - 1; index >= 0; index -= 1) {
    if (!items[index]?.disabled) {
      return index;
    }
  }

  return -1;
}
