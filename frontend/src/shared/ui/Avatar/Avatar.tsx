import type { HTMLAttributes } from 'react';
import { useEffect, useMemo, useState } from 'react';
import clsx from 'clsx';
import styles from './Avatar.module.css';

export type AvatarSize = 'sm' | 'md' | 'lg' | 'xl';
export type AvatarShape = 'circle' | 'rounded' | 'square';

export interface AvatarProps extends HTMLAttributes<HTMLSpanElement> {
  src?: string;
  alt?: string;
  name?: string;
  initials?: string;
  size?: AvatarSize;
  shape?: AvatarShape;
}

function getInitials(name?: string) {
  if (!name) return '';

  return name
    .trim()
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word[0])
    .join('')
    .toUpperCase();
}

function getFallbackText(initials?: string, name?: string) {
  const value = initials?.trim();

  if (value) return value.slice(0, 2).toUpperCase();

  return getInitials(name) || '?';
}

export function Avatar({
  src,
  alt,
  name,
  initials,
  size = 'md',
  shape = 'circle',
  className,
  ...props
}: AvatarProps) {
  const [imageFailed, setImageFailed] = useState(false);

  useEffect(() => {
    setImageFailed(false);
  }, [src]);

  const fallbackText = useMemo(
    () => getFallbackText(initials, name),
    [initials, name],
  );

  const hasImage = Boolean(src && !imageFailed);
  const accessibleLabel = alt ?? name ?? fallbackText;

  return (
    <span
      className={clsx(styles.avatar, styles[size], styles[shape], className)}
      {...(!hasImage ? { role: 'img', 'aria-label': accessibleLabel } : {})}
      {...props}
    >
      {hasImage ? (
        <img
          className={styles.image}
          src={src}
          alt={alt ?? name ?? ''}
          onError={() => setImageFailed(true)}
        />
      ) : (
        <span className={styles.fallback} aria-hidden="true">
          {fallbackText}
        </span>
      )}
    </span>
  );
}