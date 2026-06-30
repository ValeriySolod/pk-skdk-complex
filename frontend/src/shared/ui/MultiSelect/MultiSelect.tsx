import {
  useCallback,
  useEffect,
  useId,
  useMemo,
  useRef,
  useState,
  type KeyboardEvent,
} from 'react';
import clsx from 'clsx';
import styles from './MultiSelect.module.css';

export interface MultiSelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface MultiSelectProps {
  options: MultiSelectOption[];
  value: string[];
  onChange: (value: string[]) => void;
  placeholder?: string;
  label?: string;
  disabled?: boolean;
  error?: string;
  className?: string;
}

export function MultiSelect({
  options,
  value,
  onChange,
  placeholder = 'Select options',
  label,
  disabled = false,
  error,
  className,
}: MultiSelectProps) {
  const generatedId = useId();
  const triggerId = `${generatedId}-trigger`;
  const listboxId = `${generatedId}-listbox`;
  const errorId = error ? `${generatedId}-error` : undefined;
  const wrapperRef = useRef<HTMLDivElement>(null);
  const optionRefs = useRef<Array<HTMLLIElement | null>>([]);
  const [open, setOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(0);

  const selectedValues = useMemo(() => new Set(value), [value]);
  const selectedOptions = useMemo(
    () => options.filter((option) => selectedValues.has(option.value)),
    [options, selectedValues],
  );

  const firstEnabledIndex = useMemo(
    () => options.findIndex((option) => !option.disabled),
    [options],
  );

  const closeDropdown = useCallback(() => {
    setOpen(false);
  }, []);

  const openDropdown = useCallback(() => {
    if (disabled) {
      return;
    }

    setActiveIndex((currentIndex) => {
      if (options[currentIndex] && !options[currentIndex].disabled) {
        return currentIndex;
      }

      return Math.max(firstEnabledIndex, 0);
    });
    setOpen(true);
  }, [disabled, firstEnabledIndex, options]);

  const updateValue = useCallback((option: MultiSelectOption) => {
    if (disabled || option.disabled) {
      return;
    }

    if (selectedValues.has(option.value)) {
      onChange(value.filter((selectedValue) => selectedValue !== option.value));
      return;
    }

    onChange([...value, option.value]);
  }, [disabled, onChange, selectedValues, value]);

  const moveActiveIndex = useCallback((direction: 1 | -1) => {
    if (options.length === 0) {
      return;
    }

    setActiveIndex((currentIndex) => {
      for (let step = 1; step <= options.length; step += 1) {
        const nextIndex = (currentIndex + direction * step + options.length) % options.length;

        if (!options[nextIndex].disabled) {
          return nextIndex;
        }
      }

      return currentIndex;
    });
  }, [options]);

  useEffect(() => {
    if (!open) {
      return undefined;
    }

    function handlePointerDown(event: PointerEvent) {
      if (!wrapperRef.current?.contains(event.target as Node)) {
        closeDropdown();
      }
    }

    document.addEventListener('pointerdown', handlePointerDown);

    return () => {
      document.removeEventListener('pointerdown', handlePointerDown);
    };
  }, [closeDropdown, open]);

  useEffect(() => {
    if (!open) {
      return;
    }

    optionRefs.current[activeIndex]?.focus();
  }, [activeIndex, open]);

  useEffect(() => {
    if (disabled) {
      closeDropdown();
    }
  }, [closeDropdown, disabled]);

  function handleTriggerKeyDown(event: KeyboardEvent<HTMLButtonElement>) {
    if (disabled) {
      return;
    }

    if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      event.preventDefault();
      openDropdown();
      setActiveIndex(Math.max(firstEnabledIndex, 0));
    }

    if (event.key === 'Escape') {
      closeDropdown();
    }
  }

  function handleOptionKeyDown(event: KeyboardEvent<HTMLLIElement>, option: MultiSelectOption) {
    if (event.key === 'Escape') {
      event.preventDefault();
      closeDropdown();
      document.getElementById(triggerId)?.focus();
      return;
    }

    if (event.key === 'ArrowDown') {
      event.preventDefault();
      moveActiveIndex(1);
      return;
    }

    if (event.key === 'ArrowUp') {
      event.preventDefault();
      moveActiveIndex(-1);
      return;
    }

    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      updateValue(option);
    }
  }

  return (
    <div ref={wrapperRef} className={clsx(styles.field, className)}>
      {label && (
        <label className={styles.label} htmlFor={triggerId}>
          {label}
        </label>
      )}

      <button
        id={triggerId}
        type="button"
        className={clsx(
          styles.trigger,
          open && styles.triggerOpen,
          error && styles.triggerError,
        )}
        disabled={disabled}
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-controls={open ? listboxId : undefined}
        aria-invalid={error ? 'true' : undefined}
        aria-describedby={errorId}
        onClick={() => {
          if (open) {
            closeDropdown();
            return;
          }

          openDropdown();
        }}
        onKeyDown={handleTriggerKeyDown}
      >
        <span className={styles.value}>
          {selectedOptions.length > 0 ? (
            selectedOptions.map((option) => (
              <span key={option.value} className={styles.chip}>
                {option.label}
              </span>
            ))
          ) : (
            <span className={styles.placeholder}>{placeholder}</span>
          )}
        </span>
        <span className={styles.chevron} aria-hidden="true" />
      </button>

      {open && (
        <div className={styles.dropdown}>
          {options.length > 0 ? (
            <ul
              id={listboxId}
              className={styles.list}
              role="listbox"
              aria-multiselectable="true"
              aria-labelledby={triggerId}
            >
              {options.map((option, index) => {
                const selected = selectedValues.has(option.value);
                const isDisabled = Boolean(option.disabled);

                return (
                  <li
                    key={option.value}
                    ref={(node) => {
                      optionRefs.current[index] = node;
                    }}
                    className={clsx(
                      styles.option,
                      selected && styles.optionSelected,
                      isDisabled && styles.optionDisabled,
                    )}
                    role="option"
                    aria-selected={selected}
                    aria-disabled={isDisabled ? 'true' : undefined}
                    tabIndex={index === activeIndex && !isDisabled ? 0 : -1}
                    onClick={isDisabled ? undefined : () => updateValue(option)}
                    onKeyDown={(event) => handleOptionKeyDown(event, option)}
                    onMouseEnter={isDisabled ? undefined : () => setActiveIndex(index)}
                  >
                    <span className={styles.optionLabel}>{option.label}</span>
                    {selected && <span className={styles.checkmark} aria-hidden="true" />}
                  </li>
                );
              })}
            </ul>
          ) : (
            <div className={styles.empty} role="status">
              No options
            </div>
          )}
        </div>
      )}

      {error && (
        <p className={styles.errorText} id={errorId}>
          {error}
        </p>
      )}
    </div>
  );
}
