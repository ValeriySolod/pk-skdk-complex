import {
  Children,
  useId,
  type CSSProperties,
  type KeyboardEvent,
  type ReactNode,
} from 'react';
import clsx from 'clsx';

import styles from './Carousel.module.css';

export interface CarouselProps {
  children: ReactNode;
  current: number;
  onChange: (index: number) => void;
  showArrows?: boolean;
  showDots?: boolean;
  loop?: boolean;
  className?: string;
}

type TrackStyle = CSSProperties & {
  '--carousel-current': number;
};

function clampIndex(index: number, length: number) {
  return Math.min(Math.max(index, 0), length - 1);
}

function normalizeIndex(index: number, length: number) {
  return ((index % length) + length) % length;
}

export function Carousel({
  children,
  current,
  onChange,
  showArrows = true,
  showDots = true,
  loop = false,
  className,
}: CarouselProps) {
  const carouselId = useId();
  const slides = Children.toArray(children);
  const slideCount = slides.length;

  if (slideCount === 0) {
    return null;
  }

  const activeIndex = loop
    ? normalizeIndex(current, slideCount)
    : clampIndex(current, slideCount);
  const canMovePrevious = loop ? slideCount > 1 : activeIndex > 0;
  const canMoveNext = loop ? slideCount > 1 : activeIndex < slideCount - 1;
  const trackStyle: TrackStyle = {
    '--carousel-current': activeIndex,
  };

  function getPreviousIndex() {
    if (loop) {
      return normalizeIndex(activeIndex - 1, slideCount);
    }

    return clampIndex(activeIndex - 1, slideCount);
  }

  function getNextIndex() {
    if (loop) {
      return normalizeIndex(activeIndex + 1, slideCount);
    }

    return clampIndex(activeIndex + 1, slideCount);
  }

  function changeTo(index: number) {
    if (index !== activeIndex) {
      onChange(index);
    }
  }

  function handlePrevious() {
    if (canMovePrevious) {
      changeTo(getPreviousIndex());
    }
  }

  function handleNext() {
    if (canMoveNext) {
      changeTo(getNextIndex());
    }
  }

  function handleKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    switch (event.key) {
      case 'ArrowLeft':
        event.preventDefault();
        handlePrevious();
        break;
      case 'ArrowRight':
        event.preventDefault();
        handleNext();
        break;
      case 'Home':
        event.preventDefault();
        changeTo(0);
        break;
      case 'End':
        event.preventDefault();
        changeTo(slideCount - 1);
        break;
      default:
        break;
    }
  }

  return (
    <section
      className={clsx(styles.carousel, className)}
      tabIndex={0}
      aria-roledescription="carousel"
      onKeyDown={handleKeyDown}
    >
      <div className={styles.viewport}>
        <div className={styles.track} style={trackStyle}>
          {slides.map((slide, index) => (
            <div
              id={`${carouselId}-slide-${index}`}
              className={styles.slide}
              role="tabpanel"
              aria-hidden={index !== activeIndex}
              aria-labelledby={`${carouselId}-dot-${index}`}
              key={index}
            >
              {slide}
            </div>
          ))}
        </div>
      </div>

      {(showArrows || showDots) && (
        <div className={styles.controls}>
          {showArrows && (
            <button
              className={styles.arrow}
              type="button"
              aria-label="Previous slide"
              disabled={!canMovePrevious}
              onClick={handlePrevious}
            >
              <span aria-hidden="true">&lt;</span>
            </button>
          )}

          {showDots && (
            <div className={styles.dots} role="tablist" aria-label="Carousel slides">
              {slides.map((_, index) => {
                const selected = index === activeIndex;

                return (
                  <button
                    id={`${carouselId}-dot-${index}`}
                    className={clsx(styles.dot, selected && styles.activeDot)}
                    type="button"
                    role="tab"
                    aria-selected={selected}
                    aria-controls={`${carouselId}-slide-${index}`}
                    aria-label={`Go to slide ${index + 1}`}
                    tabIndex={selected ? 0 : -1}
                    key={index}
                    onClick={() => changeTo(index)}
                  />
                );
              })}
            </div>
          )}

          {showArrows && (
            <button
              className={styles.arrow}
              type="button"
              aria-label="Next slide"
              disabled={!canMoveNext}
              onClick={handleNext}
            >
              <span aria-hidden="true">&gt;</span>
            </button>
          )}
        </div>
      )}
    </section>
  );
}
