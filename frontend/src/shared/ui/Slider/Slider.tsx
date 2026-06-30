import type { CSSProperties, ChangeEvent } from 'react';

import styles from './Slider.module.css';

export interface SliderProps {
  value: number;
  min?: number;
  max?: number;
  step?: number;
  disabled?: boolean;
  onChange?: (value: number) => void;
  className?: string;
}

type SliderStyle = CSSProperties & {
  '--slider-progress': string;
};

function clampValue(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max);
}

function getProgress(value: number, min: number, max: number) {
  if (max <= min) {
    return 0;
  }

  return ((clampValue(value, min, max) - min) / (max - min)) * 100;
}

export function Slider({
  value,
  min = 0,
  max = 100,
  step = 1,
  disabled = false,
  onChange,
  className,
}: SliderProps) {
  const progress = getProgress(value, min, max);
  const sliderStyle: SliderStyle = {
    '--slider-progress': `${progress}%`,
  };
  const sliderClassName = [styles.slider, className].filter(Boolean).join(' ');

  function handleChange(event: ChangeEvent<HTMLInputElement>) {
    onChange?.(event.currentTarget.valueAsNumber);
  }

  return (
    <input
      className={sliderClassName}
      style={sliderStyle}
      type="range"
      value={value}
      min={min}
      max={max}
      step={step}
      disabled={disabled}
      aria-disabled={disabled || undefined}
      onChange={handleChange}
    />
  );
}
