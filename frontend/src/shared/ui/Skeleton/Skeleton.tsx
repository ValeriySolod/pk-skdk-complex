import styles from './Skeleton.module.css';

type SkeletonVariant = 'text' | 'rect' | 'circle';

type SkeletonProps = {
  variant?: SkeletonVariant;
  width?: string | number;
  height?: string | number;
  lines?: number;
  animated?: boolean;
  className?: string;
};

const DEFAULT_TEXT_HEIGHT = '1rem';

function toCssSize(value: string | number | undefined): string | undefined {
  if (typeof value === 'number') {
    return `${value}px`;
  }

  return value;
}

function getLineCount(lines: number | undefined): number {
  if (typeof lines !== 'number' || !Number.isFinite(lines)) {
    return 1;
  }

  return Math.max(1, Math.floor(lines));
}

export function Skeleton({
  variant = 'rect',
  width,
  height,
  lines = 1,
  animated = true,
  className,
}: SkeletonProps) {
  const classes = [
    styles.skeleton,
    styles[variant],
    animated ? styles.animated : undefined,
    className,
  ]
    .filter(Boolean)
    .join(' ');

  const style = {
    width: toCssSize(width),
    height: toCssSize(height ?? (variant === 'text' ? DEFAULT_TEXT_HEIGHT : undefined)),
  };

  if (variant === 'text') {
    return (
      <span className={styles.textGroup} aria-hidden="true">
        {Array.from({ length: getLineCount(lines) }, (_, index) => (
          <span key={index} className={classes} style={style} />
        ))}
      </span>
    );
  }

  return <span className={classes} style={style} aria-hidden="true" />;
}

export type { SkeletonProps, SkeletonVariant };
