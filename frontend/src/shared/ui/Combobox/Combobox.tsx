import {
  useCallback,
  useEffect,
  useId,
  useMemo,
  useRef,
  useState,
  type ChangeEvent,
  type KeyboardEvent,
} from 'react';
import clsx from 'clsx';

import styles from './Combobox.module.css';

export interface ComboboxOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface ComboboxProps {
  options: ComboboxOption[];
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  label?: string;
  disabled?: boolean;
  error?: string;
  helperText?: string;
  emptyText?: string;
  className?: string;
}

export function Combobox({
  options,
  value,
  onChange,
  placeholder,
  label,
  disabled = false,
  error,
  helperText,
  emptyText = 'No options',
  className,
}: ComboboxProps) {
  const generatedId = useId();
  const inputId = `${generatedId}-input`;
  const listboxId = `${generatedId}-listbox`;
  const helperTextId = helperText ? `${generatedId}-helper` : undefined;
  const errorId = error ? `${generatedId}-error` : undefined;
  const describedBy = error ? errorId : helperText ? helperTextId : undefined;
  const wrapperRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const [open, setOpen] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [activeIndex, setActiveIndex] = useState(-1);

  const selectedOption = useMemo(
    () => options.find((option) => option.value === value),
    [options, value],
  );
  const selectedLabel = selectedOption?.label ?? '';

  const filteredOptions = useMemo(() => {
    const query = inputValue.trim().toLocaleLowerCase();

    if (!query) {
      return options;
    }

    return options.filter((option) => option.label.toLocaleLowerCase().includes(query));
  }, [inputValue, options]);

  const activeOption = activeIndex >= 0 ? filteredOptions[activeIndex] : undefined;
  const activeOptionId = activeOption ? `${generatedId}-option-${activeIndex}` : undefined;

  const findEnabledIndex = useCallback(
    (startIndex: number, direction: 1 | -1) => {
      if (filteredOptions.length === 0) {
        return -1;
      }

      const normalizedStartIndex =
        (startIndex + filteredOptions.length) % filteredOptions.length;

      for (let step = 0; step < filteredOptions.length; step += 1) {
        const nextIndex =
          (normalizedStartIndex + direction * step + filteredOptions.length) %
          filteredOptions.length;

        if (!filteredOptions[nextIndex].disabled) {
          return nextIndex;
        }
      }

      return -1;
    },
    [filteredOptions],
  );

  const firstEnabledIndex = useMemo(() => findEnabledIndex(0, 1), [findEnabledIndex]);
  const lastEnabledIndex = useMemo(
    () => findEnabledIndex(filteredOptions.length - 1, -1),
    [filteredOptions.length, findEnabledIndex],
  );

  const closeListbox = useCallback(() => {
    setOpen(false);
    setActiveIndex(-1);
  }, []);

  const openListbox = useCallback(() => {
    if (disabled) {
      return;
    }

    setOpen(true);
    setActiveIndex((currentIndex) => {
      if (
        currentIndex >= 0 &&
        filteredOptions[currentIndex] &&
        !filteredOptions[currentIndex].disabled
      ) {
        return currentIndex;
      }

      return firstEnabledIndex;
    });
  }, [disabled, filteredOptions, firstEnabledIndex]);

  const selectOption = useCallback(
    (option: ComboboxOption | undefined) => {
      if (!option || option.disabled || disabled) {
        return;
      }

      setInputValue(option.label);
      onChange(option.value);
      closeListbox();
      inputRef.current?.focus();
    },
    [closeListbox, disabled, onChange],
  );

  const moveActiveIndex = useCallback(
    (direction: 1 | -1) => {
      if (!open) {
        openListbox();
        return;
      }

      setActiveIndex((currentIndex) => {
        const startIndex = currentIndex < 0 ? firstEnabledIndex : currentIndex + direction;
        return findEnabledIndex(startIndex, direction);
      });
    },
    [findEnabledIndex, firstEnabledIndex, open, openListbox],
  );

  useEffect(() => {
    setInputValue(selectedLabel);
  }, [selectedLabel]);

  useEffect(() => {
    if (!open) {
      return;
    }

    setActiveIndex((currentIndex) => {
      if (
        currentIndex >= 0 &&
        filteredOptions[currentIndex] &&
        !filteredOptions[currentIndex].disabled
      ) {
        return currentIndex;
      }

      return firstEnabledIndex;
    });
  }, [filteredOptions, firstEnabledIndex, open]);

  useEffect(() => {
    if (!open) {
      return undefined;
    }

    function handlePointerDown(event: PointerEvent) {
      if (!wrapperRef.current?.contains(event.target as Node)) {
        setInputValue(selectedLabel);
        closeListbox();
      }
    }

    document.addEventListener('pointerdown', handlePointerDown);

    return () => {
      document.removeEventListener('pointerdown', handlePointerDown);
    };
  }, [closeListbox, open, selectedLabel]);

  useEffect(() => {
    if (disabled) {
      closeListbox();
    }
  }, [closeListbox, disabled]);

  function handleInputChange(event: ChangeEvent<HTMLInputElement>) {
    setInputValue(event.target.value);
    setOpen(true);
  }

  function handleKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (disabled) {
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

    if (event.key === 'Home') {
      event.preventDefault();
      openListbox();
      setActiveIndex(firstEnabledIndex);
      return;
    }

    if (event.key === 'End') {
      event.preventDefault();
      openListbox();
      setActiveIndex(lastEnabledIndex);
      return;
    }

    if (event.key === 'Enter') {
      if (open) {
        event.preventDefault();
        selectOption(activeOption);
      }

      return;
    }

    if (event.key === 'Escape') {
      event.preventDefault();
      setInputValue(selectedLabel);
      closeListbox();
    }
  }

  return (
    <div ref={wrapperRef} className={clsx(styles.field, className)}>
      {label ? (
        <label className={styles.label} htmlFor={inputId}>
          {label}
        </label>
      ) : null}

      <div className={styles.control}>
        <input
          ref={inputRef}
          id={inputId}
          className={clsx(styles.input, error && styles.invalid)}
          type="text"
          role="combobox"
          value={inputValue}
          placeholder={placeholder}
          disabled={disabled}
          autoComplete="off"
          aria-autocomplete="list"
          aria-expanded={open}
          aria-controls={listboxId}
          aria-activedescendant={open ? activeOptionId : undefined}
          aria-invalid={error ? true : undefined}
          aria-describedby={describedBy}
          onChange={handleInputChange}
          onFocus={openListbox}
          onKeyDown={handleKeyDown}
        />
        <span className={styles.chevron} aria-hidden="true" />

        {open ? (
          <div className={styles.dropdown}>
            {filteredOptions.length > 0 ? (
              <ul id={listboxId} className={styles.list} role="listbox">
                {filteredOptions.map((option, index) => {
                  const selected = option.value === value;
                  const isActive = index === activeIndex;
                  const isDisabled = Boolean(option.disabled);
                  const optionId = `${generatedId}-option-${index}`;

                  return (
                    <li
                      key={option.value}
                      id={optionId}
                      className={clsx(
                        styles.option,
                        isActive && styles.optionActive,
                        selected && styles.optionSelected,
                        isDisabled && styles.optionDisabled,
                      )}
                      role="option"
                      aria-selected={selected}
                      aria-disabled={isDisabled ? 'true' : undefined}
                      onMouseDown={(event) => event.preventDefault()}
                      onClick={isDisabled ? undefined : () => selectOption(option)}
                      onMouseEnter={isDisabled ? undefined : () => setActiveIndex(index)}
                    >
                      <span className={styles.optionLabel}>{option.label}</span>
                      {selected ? <span className={styles.checkmark} aria-hidden="true" /> : null}
                    </li>
                  );
                })}
              </ul>
            ) : (
              <div className={styles.empty} role="status">
                {emptyText}
              </div>
            )}
          </div>
        ) : null}
      </div>

      {error ? (
        <p className={styles.errorText} id={errorId}>
          {error}
        </p>
      ) : helperText ? (
        <p className={styles.helperText} id={helperTextId}>
          {helperText}
        </p>
      ) : null}
    </div>
  );
}
