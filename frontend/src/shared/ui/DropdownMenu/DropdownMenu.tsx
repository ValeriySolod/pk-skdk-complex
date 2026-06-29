import {
  useEffect,
  useId,
  useRef,
  useState,
  type KeyboardEvent,
  type ReactNode,
} from 'react';
import clsx from 'clsx';
import styles from './DropdownMenu.module.css';

export type DropdownMenuAlign = 'start' | 'end';

export interface DropdownMenuItem {
  id: string;
  label: ReactNode;
  onSelect: () => void;
  disabled?: boolean;
  destructive?: boolean;
}

export interface DropdownMenuProps {
  trigger: ReactNode;
  items: DropdownMenuItem[];
  align?: DropdownMenuAlign;
  disabled?: boolean;
  className?: string;
  menuClassName?: string;
}

export function DropdownMenu({
  trigger,
  items,
  align = 'start',
  disabled = false,
  className,
  menuClassName,
}: DropdownMenuProps) {
  const menuId = useId();
  const wrapperRef = useRef<HTMLDivElement>(null);
  const itemRefs = useRef<Array<HTMLButtonElement | null>>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);

  const enabledItems = items.filter((item) => !item.disabled);
  const hasEnabledItems = enabledItems.length > 0;

  useEffect(() => {
    if (!isOpen) {
      return undefined;
    }

    function handlePointerDown(event: PointerEvent) {
      if (!wrapperRef.current?.contains(event.target as Node)) {
        setIsOpen(false);
        setActiveIndex(-1);
      }
    }

    document.addEventListener('pointerdown', handlePointerDown);

    return () => {
      document.removeEventListener('pointerdown', handlePointerDown);
    };
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen || activeIndex < 0) {
      return;
    }

    itemRefs.current[activeIndex]?.focus();
  }, [activeIndex, isOpen]);

  function getNextEnabledIndex(currentIndex: number, direction: 1 | -1) {
    if (!hasEnabledItems) {
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

  function openMenu(initialIndex: number) {
    if (disabled || items.length === 0) {
      return;
    }

    setIsOpen(true);
    setActiveIndex(initialIndex);
  }

  function closeMenu() {
    setIsOpen(false);
    setActiveIndex(-1);
  }

  function handleTriggerKeyDown(event: KeyboardEvent<HTMLButtonElement>) {
    if (disabled) {
      return;
    }

    if (event.key === 'ArrowDown') {
      event.preventDefault();
      openMenu(getNextEnabledIndex(-1, 1));
    }

    if (event.key === 'ArrowUp') {
      event.preventDefault();
      openMenu(getNextEnabledIndex(0, -1));
    }
  }

  function handleMenuKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    if (event.key === 'Escape') {
      event.preventDefault();
      closeMenu();
      return;
    }

    if (event.key === 'ArrowDown') {
      event.preventDefault();
      setActiveIndex((currentIndex) => getNextEnabledIndex(currentIndex, 1));
      return;
    }

    if (event.key === 'ArrowUp') {
      event.preventDefault();
      setActiveIndex((currentIndex) => getNextEnabledIndex(currentIndex, -1));
      return;
    }

    if (event.key === 'Home') {
      event.preventDefault();
      setActiveIndex(getNextEnabledIndex(-1, 1));
      return;
    }

    if (event.key === 'End') {
      event.preventDefault();
      setActiveIndex(getNextEnabledIndex(0, -1));
    }
  }

  function handleItemSelect(item: DropdownMenuItem) {
    if (item.disabled) {
      return;
    }

    item.onSelect();
    closeMenu();
  }

  return (
    <div ref={wrapperRef} className={clsx(styles.wrapper, className)}>
      <button
        type="button"
        className={styles.trigger}
        aria-haspopup="menu"
        aria-expanded={isOpen}
        aria-controls={isOpen ? menuId : undefined}
        disabled={disabled}
        onClick={() => {
          if (isOpen) {
            closeMenu();
            return;
          }

          openMenu(getNextEnabledIndex(-1, 1));
        }}
        onKeyDown={handleTriggerKeyDown}
      >
        {trigger}
      </button>

      {isOpen && (
        <div
          id={menuId}
          role="menu"
          className={clsx(styles.menu, styles[align], menuClassName)}
          onKeyDown={handleMenuKeyDown}
        >
          {items.map((item, index) => (
            <button
              key={item.id}
              ref={(element) => {
                itemRefs.current[index] = element;
              }}
              type="button"
              role="menuitem"
              className={clsx(styles.item, item.destructive && styles.destructive)}
              disabled={item.disabled}
              tabIndex={index === activeIndex ? 0 : -1}
              onClick={() => handleItemSelect(item)}
              onMouseEnter={() => {
                if (!item.disabled) {
                  setActiveIndex(index);
                }
              }}
            >
              {item.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
