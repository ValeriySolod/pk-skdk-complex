import {
  useEffect,
  useId,
  useLayoutEffect,
  useRef,
  useState,
  type CSSProperties,
  type KeyboardEvent,
  type MouseEvent,
  type ReactNode,
} from 'react';
import clsx from 'clsx';
import styles from './ContextMenu.module.css';

export interface ContextMenuItem {
  id: string;
  label: ReactNode;
  icon?: ReactNode;
  disabled?: boolean;
  danger?: boolean;
  onSelect?: () => void;
}

export interface ContextMenuProps {
  items: ContextMenuItem[];
  children: ReactNode;
  disabled?: boolean;
  className?: string;
}

interface MenuPosition {
  x: number;
  y: number;
}

const VIEWPORT_PADDING = 8;

export function ContextMenu({
  items,
  children,
  disabled = false,
  className,
}: ContextMenuProps) {
  const menuId = useId();
  const wrapperRef = useRef<HTMLDivElement>(null);
  const menuRef = useRef<HTMLUListElement>(null);
  const itemRefs = useRef<Array<HTMLButtonElement | null>>([]);
  const [position, setPosition] = useState<MenuPosition | null>(null);
  const [activeIndex, setActiveIndex] = useState(() => getFirstEnabledIndex(items));

  const isOpen = position !== null;
  const focusableIndex = isEnabledItem(items, activeIndex)
    ? activeIndex
    : getFirstEnabledIndex(items);

  useEffect(() => {
    if (!isOpen) {
      return undefined;
    }

    function handlePointerDown(event: PointerEvent) {
      if (!wrapperRef.current?.contains(event.target as Node)) {
        closeMenu();
      }
    }

    function handleKeyDown(event: globalThis.KeyboardEvent) {
      if (event.key === 'Escape') {
        event.preventDefault();
        closeMenu();
      }
    }

    document.addEventListener('pointerdown', handlePointerDown);
    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('pointerdown', handlePointerDown);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen]);

  useEffect(() => {
    if (!isEnabledItem(items, activeIndex)) {
      setActiveIndex(getFirstEnabledIndex(items));
    }
  }, [activeIndex, items]);

  useLayoutEffect(() => {
    if (!position || !menuRef.current) {
      return;
    }

    const menuRect = menuRef.current.getBoundingClientRect();
    const nextX = clamp(
      position.x,
      VIEWPORT_PADDING,
      Math.max(VIEWPORT_PADDING, window.innerWidth - menuRect.width - VIEWPORT_PADDING),
    );
    const nextY = clamp(
      position.y,
      VIEWPORT_PADDING,
      Math.max(VIEWPORT_PADDING, window.innerHeight - menuRect.height - VIEWPORT_PADDING),
    );

    if (nextX !== position.x || nextY !== position.y) {
      setPosition({ x: nextX, y: nextY });
    }
  }, [position]);

  useEffect(() => {
    if (!isOpen || focusableIndex < 0) {
      return;
    }

    requestAnimationFrame(() => {
      itemRefs.current[focusableIndex]?.focus();
    });
  }, [focusableIndex, isOpen]);

  if (items.length === 0) {
    return null;
  }

  function closeMenu() {
    setPosition(null);
    wrapperRef.current?.focus();
  }

  function openMenu(nextPosition: MenuPosition) {
    if (disabled) {
      return;
    }

    setActiveIndex(getFirstEnabledIndex(items));
    setPosition(nextPosition);
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

  function handleContextMenu(event: MouseEvent<HTMLDivElement>) {
    if (disabled) {
      return;
    }

    event.preventDefault();
    openMenu({ x: event.clientX, y: event.clientY });
  }

  function handleMenuKeyDown(event: KeyboardEvent<HTMLUListElement>) {
    const target = event.target instanceof HTMLButtonElement ? event.target : null;
    const currentIndex = Number(target?.dataset.contextMenuIndex ?? focusableIndex);
    const safeCurrentIndex = Number.isNaN(currentIndex) ? focusableIndex : currentIndex;

    switch (event.key) {
      case 'Escape':
        event.preventDefault();
        closeMenu();
        break;
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
        const firstEnabledIndex = getFirstEnabledIndex(items);

        if (firstEnabledIndex >= 0) {
          focusItem(firstEnabledIndex);
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
      default:
        break;
    }
  }

  function handleSelect(item: ContextMenuItem) {
    if (item.disabled) {
      return;
    }

    item.onSelect?.();
    closeMenu();
  }

  const menuStyle: CSSProperties | undefined = position
    ? {
        left: position.x,
        top: position.y,
      }
    : undefined;

  return (
    <div
      ref={wrapperRef}
      className={clsx(styles.wrapper, className)}
      aria-haspopup="menu"
      aria-expanded={isOpen}
      aria-disabled={disabled || undefined}
      tabIndex={0}
      onContextMenu={handleContextMenu}
    >
      {children}

      {isOpen && (
        <ul
          ref={menuRef}
          id={menuId}
          className={styles.menu}
          style={menuStyle}
          role="menu"
          aria-orientation="vertical"
          onKeyDown={handleMenuKeyDown}
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
                data-context-menu-index={index}
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
      )}
    </div>
  );
}

function isEnabledItem(items: ContextMenuItem[], index: number) {
  return index >= 0 && index < items.length && !items[index]?.disabled;
}

function getFirstEnabledIndex(items: ContextMenuItem[]) {
  return items.findIndex((item) => !item.disabled);
}

function getLastEnabledIndex(items: ContextMenuItem[]) {
  for (let index = items.length - 1; index >= 0; index -= 1) {
    if (!items[index]?.disabled) {
      return index;
    }
  }

  return -1;
}

function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max);
}
