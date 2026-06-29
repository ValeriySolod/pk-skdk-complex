import styles from './Spacer.module.css';

export type SpacerSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

export interface SpacerProps {
  size?: SpacerSize;
  axis?: 'vertical' | 'horizontal';
  className?: string;
}

export function Spacer({
  size = 'md',
  axis = 'vertical',
  className,
}: SpacerProps) {
  const spacerClassName = [styles.spacer, styles[size], styles[axis], className]
    .filter(Boolean)
    .join(' ');

  return (
    <span
      className={spacerClassName}
      aria-hidden="true"
    />
  );
}
