import styles from './Avatar.module.css';

export type AvatarSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

export interface AvatarProps {
  src?: string;
  alt?: string;
  name?: string;
  size?: AvatarSize;
  rounded?: boolean;
  className?: string;
}

function getInitials(name?: string) {
  if (!name?.trim()) {
    return '?';
  }

  return name
    .trim()
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word[0])
    .join('')
    .toUpperCase() || '?';
}

function getClassName(size: AvatarSize, rounded: boolean, className?: string) {
  return [
    styles.avatar,
    styles[size],
    rounded ? styles.rounded : styles.softRounded,
    className,
  ]
    .filter(Boolean)
    .join(' ');
}

export function Avatar({
  src,
  alt,
  name,
  size = 'md',
  rounded = true,
  className,
}: AvatarProps) {
  const avatarClassName = getClassName(size, rounded, className);
  const fallbackLabel = name ?? 'Avatar';

  return (
    <span
      className={avatarClassName}
      {...(!src ? { role: 'img', 'aria-label': fallbackLabel } : {})}
    >
      {src ? (
        <img className={styles.image} src={src} alt={alt ?? name ?? 'Avatar'} />
      ) : (
        <span className={styles.initials} aria-hidden="true">
          {getInitials(name)}
        </span>
      )}
    </span>
  );
}
