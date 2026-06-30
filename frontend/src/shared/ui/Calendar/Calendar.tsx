import type { HTMLAttributes, KeyboardEvent, ReactNode } from 'react';
import { useEffect, useMemo, useRef, useState } from 'react';
import clsx from 'clsx';

import styles from './Calendar.module.css';

export type CalendarWeekday = 0 | 1 | 2 | 3 | 4 | 5 | 6;

export type CalendarDateMatcher =
  | Date
  | Date[]
  | ((date: Date) => boolean);

export interface CalendarDayModifiers {
  isSelected: boolean;
  isToday: boolean;
  isOutsideMonth: boolean;
  isDisabled: boolean;
}

export interface CalendarProps
  extends Omit<HTMLAttributes<HTMLDivElement>, 'defaultValue' | 'onChange'> {
  value?: Date;
  defaultValue?: Date;
  onValueChange?: (date: Date) => void;
  month?: Date;
  defaultMonth?: Date;
  onMonthChange?: (month: Date) => void;
  minDate?: Date;
  maxDate?: Date;
  disabledDates?: CalendarDateMatcher;
  locale?: string;
  weekStartsOn?: CalendarWeekday;
  showOutsideDays?: boolean;
  disabled?: boolean;
  previousMonthLabel?: string;
  nextMonthLabel?: string;
  ariaLabel?: string;
  renderDay?: (date: Date, modifiers: CalendarDayModifiers) => ReactNode;
}

interface CalendarDay {
  date: Date;
  key: string;
  isOutsideMonth: boolean;
}

function startOfDay(date: Date) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate());
}

function startOfMonth(date: Date) {
  return new Date(date.getFullYear(), date.getMonth(), 1);
}

function addDays(date: Date, amount: number) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate() + amount);
}

function addMonths(date: Date, amount: number) {
  const targetMonth = new Date(date.getFullYear(), date.getMonth() + amount, 1);
  const lastDayOfTargetMonth = new Date(
    targetMonth.getFullYear(),
    targetMonth.getMonth() + 1,
    0,
  ).getDate();

  return new Date(
    targetMonth.getFullYear(),
    targetMonth.getMonth(),
    Math.min(date.getDate(), lastDayOfTargetMonth),
  );
}

function isSameDay(left: Date | undefined, right: Date | undefined) {
  if (!left || !right) {
    return false;
  }

  return startOfDay(left).getTime() === startOfDay(right).getTime();
}

function isSameMonth(left: Date, right: Date) {
  return (
    left.getFullYear() === right.getFullYear() &&
    left.getMonth() === right.getMonth()
  );
}

function getDateKey(date: Date) {
  const year = String(date.getFullYear());
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');

  return `${year}-${month}-${day}`;
}

function getGridStart(month: Date, weekStartsOn: CalendarWeekday) {
  const firstDay = startOfMonth(month);
  const offset = (firstDay.getDay() - weekStartsOn + 7) % 7;

  return addDays(firstDay, -offset);
}

function createCalendarDays(month: Date, weekStartsOn: CalendarWeekday) {
  const gridStart = getGridStart(month, weekStartsOn);

  return Array.from({ length: 42 }, (_, index): CalendarDay => {
    const date = addDays(gridStart, index);

    return {
      date,
      key: getDateKey(date),
      isOutsideMonth: !isSameMonth(date, month),
    };
  });
}

function createWeekdayLabels(locale: string, weekStartsOn: CalendarWeekday) {
  const baseSunday = new Date(2024, 0, 7);

  return Array.from({ length: 7 }, (_, index) => {
    const weekdayIndex = (weekStartsOn + index) % 7;
    const date = addDays(baseSunday, weekdayIndex);

    return {
      short: new Intl.DateTimeFormat(locale, { weekday: 'short' }).format(date),
      long: new Intl.DateTimeFormat(locale, { weekday: 'long' }).format(date),
    };
  });
}

function matchesDate(date: Date, matcher: CalendarDateMatcher | undefined) {
  if (!matcher) {
    return false;
  }

  if (typeof matcher === 'function') {
    return matcher(date);
  }

  if (Array.isArray(matcher)) {
    return matcher.some((matchedDate) => isSameDay(date, matchedDate));
  }

  return isSameDay(date, matcher);
}

function isDateDisabled(
  date: Date,
  minDate: Date | undefined,
  maxDate: Date | undefined,
  matcher: CalendarDateMatcher | undefined,
) {
  const currentDate = startOfDay(date).getTime();
  const minTime = minDate ? startOfDay(minDate).getTime() : undefined;
  const maxTime = maxDate ? startOfDay(maxDate).getTime() : undefined;

  return (
    (minTime !== undefined && currentDate < minTime) ||
    (maxTime !== undefined && currentDate > maxTime) ||
    matchesDate(date, matcher)
  );
}

function getFocusableDate(
  days: CalendarDay[],
  selectedDate: Date | undefined,
  today: Date,
  minDate: Date | undefined,
  maxDate: Date | undefined,
  disabledDates: CalendarDateMatcher | undefined,
) {
  const candidates = [
    selectedDate,
    isSameMonth(today, days[15].date) ? today : undefined,
    days.find((day) => !day.isOutsideMonth)?.date,
    days[0].date,
  ];

  return candidates.find(
    (date) =>
      date &&
      days.some((day) => isSameDay(day.date, date)) &&
      !isDateDisabled(date, minDate, maxDate, disabledDates),
  );
}

export function Calendar({
  value,
  defaultValue,
  onValueChange,
  month,
  defaultMonth,
  onMonthChange,
  minDate,
  maxDate,
  disabledDates,
  locale = 'uk-UA',
  weekStartsOn = 1,
  showOutsideDays = true,
  disabled = false,
  previousMonthLabel = 'Previous month',
  nextMonthLabel = 'Next month',
  ariaLabel = 'Calendar',
  renderDay,
  className,
  ...props
}: CalendarProps) {
  const rootRef = useRef<HTMLDivElement>(null);
  const today = useMemo(() => startOfDay(new Date()), []);
  const isValueControlled = value !== undefined;
  const [internalValue, setInternalValue] = useState<Date | undefined>(
    defaultValue ? startOfDay(defaultValue) : undefined,
  );
  const selectedDate = isValueControlled
    ? startOfDay(value)
    : internalValue;

  const initialMonth = defaultMonth ?? value ?? defaultValue ?? today;
  const isMonthControlled = month !== undefined;
  const [internalMonth, setInternalMonth] = useState(() =>
    startOfMonth(initialMonth),
  );
  const displayedMonth = startOfMonth(isMonthControlled ? month : internalMonth);
  const [focusDate, setFocusDate] = useState<Date | undefined>();

  const days = useMemo(
    () => createCalendarDays(displayedMonth, weekStartsOn),
    [displayedMonth, weekStartsOn],
  );
  const weekdayLabels = useMemo(
    () => createWeekdayLabels(locale, weekStartsOn),
    [locale, weekStartsOn],
  );
  const monthLabel = useMemo(
    () =>
      new Intl.DateTimeFormat(locale, {
        month: 'long',
        year: 'numeric',
      }).format(displayedMonth),
    [displayedMonth, locale],
  );
  const fullDateFormatter = useMemo(
    () =>
      new Intl.DateTimeFormat(locale, {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
      }),
    [locale],
  );
  const focusableDate = getFocusableDate(
    days,
    selectedDate,
    today,
    minDate,
    maxDate,
    disabledDates,
  );

  useEffect(() => {
    if (!focusDate) {
      return;
    }

    const key = getDateKey(focusDate);
    const button = rootRef.current?.querySelector<HTMLButtonElement>(
      `[data-calendar-day="${key}"]`,
    );

    button?.focus();
  }, [displayedMonth, focusDate]);

  function updateMonth(nextMonth: Date) {
    const normalizedMonth = startOfMonth(nextMonth);

    if (!isMonthControlled) {
      setInternalMonth(normalizedMonth);
    }

    onMonthChange?.(normalizedMonth);
  }

  function updateSelectedDate(nextDate: Date) {
    const normalizedDate = startOfDay(nextDate);

    if (!isValueControlled) {
      setInternalValue(normalizedDate);
    }

    onValueChange?.(normalizedDate);
  }

  function moveFocus(nextDate: Date) {
    setFocusDate(nextDate);

    if (!isSameMonth(nextDate, displayedMonth)) {
      updateMonth(nextDate);
    }
  }

  function handleDayKeyDown(event: KeyboardEvent<HTMLButtonElement>) {
    const currentKey = event.currentTarget.dataset.calendarDay;
    const currentDay = days.find((day) => day.key === currentKey);

    if (!currentDay) {
      return;
    }

    const keyActions: Record<string, () => Date> = {
      ArrowLeft: () => addDays(currentDay.date, -1),
      ArrowRight: () => addDays(currentDay.date, 1),
      ArrowUp: () => addDays(currentDay.date, -7),
      ArrowDown: () => addDays(currentDay.date, 7),
      Home: () =>
        addDays(
          currentDay.date,
          -((currentDay.date.getDay() - weekStartsOn + 7) % 7),
        ),
      End: () =>
        addDays(
          currentDay.date,
          6 - ((currentDay.date.getDay() - weekStartsOn + 7) % 7),
        ),
      PageUp: () => addMonths(currentDay.date, event.shiftKey ? -12 : -1),
      PageDown: () => addMonths(currentDay.date, event.shiftKey ? 12 : 1),
    };

    const getNextDate = keyActions[event.key];

    if (!getNextDate) {
      return;
    }

    event.preventDefault();
    moveFocus(getNextDate());
  }

  function handleSelectDate(date: Date) {
    if (disabled || isDateDisabled(date, minDate, maxDate, disabledDates)) {
      return;
    }

    updateSelectedDate(date);
    setFocusDate(date);

    if (!isSameMonth(date, displayedMonth)) {
      updateMonth(date);
    }
  }

  return (
    <div
      ref={rootRef}
      className={clsx(styles.calendar, disabled && styles.disabled, className)}
      role="group"
      aria-label={ariaLabel}
      {...props}
    >
      <div className={styles.header}>
        <button
          className={styles.navButton}
          type="button"
          aria-label={previousMonthLabel}
          disabled={disabled}
          onClick={() => updateMonth(addMonths(displayedMonth, -1))}
        >
          <span aria-hidden="true">‹</span>
        </button>

        <div className={styles.monthLabel} aria-live="polite">
          {monthLabel}
        </div>

        <button
          className={styles.navButton}
          type="button"
          aria-label={nextMonthLabel}
          disabled={disabled}
          onClick={() => updateMonth(addMonths(displayedMonth, 1))}
        >
          <span aria-hidden="true">›</span>
        </button>
      </div>

      <table className={styles.grid} role="grid" aria-readonly="true">
        <thead>
          <tr>
            {weekdayLabels.map((weekday) => (
              <th className={styles.weekday} scope="col" key={weekday.long}>
                <abbr title={weekday.long}>{weekday.short}</abbr>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {Array.from({ length: 6 }, (_, weekIndex) => (
            <tr key={weekIndex}>
              {days.slice(weekIndex * 7, weekIndex * 7 + 7).map((day) => {
                const isSelected = isSameDay(day.date, selectedDate);
                const isToday = isSameDay(day.date, today);
                const isDisabled =
                  disabled ||
                  isDateDisabled(day.date, minDate, maxDate, disabledDates);
                const isHiddenOutsideDay =
                  day.isOutsideMonth && !showOutsideDays;
                const modifiers: CalendarDayModifiers = {
                  isSelected,
                  isToday,
                  isOutsideMonth: day.isOutsideMonth,
                  isDisabled,
                };
                const canReceiveTab =
                  focusableDate !== undefined && isSameDay(day.date, focusableDate);

                return (
                  <td className={styles.dayCell} role="gridcell" key={day.key}>
                    {!isHiddenOutsideDay && (
                      <button
                        className={clsx(
                          styles.dayButton,
                          day.isOutsideMonth && styles.outsideMonth,
                          isSelected && styles.selected,
                          isToday && styles.today,
                        )}
                        type="button"
                        data-calendar-day={day.key}
                        disabled={isDisabled}
                        tabIndex={canReceiveTab ? 0 : -1}
                        aria-label={fullDateFormatter.format(day.date)}
                        aria-pressed={isSelected}
                        onClick={() => handleSelectDate(day.date)}
                        onKeyDown={handleDayKeyDown}
                      >
                        {renderDay
                          ? renderDay(day.date, modifiers)
                          : day.date.getDate()}
                      </button>
                    )}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
