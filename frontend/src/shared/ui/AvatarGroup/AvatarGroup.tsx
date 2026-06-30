import styles from './AvatarGroup.module.css';

export interface AvatarGroupItem {
  id: string;
  name: string;
  src?: string;
  initials?: string;
}

export interface AvatarGroupProps {
  items: AvatarGroupItem[];
  max?: number;
  size?: 'sm' | 'md' | 'lg';
  overlap?: 'sm' | 'md' | 'lg';
  className?: string;
}

function getInitials(name: string) {
  const trimmedName = name.trim();

  if (!trimmedName) {
    return '?';
  }

  return (
    trimmedName
      .split(/\s+/)
      .slice(0, 2)
      .map((word) => word[0])
      .join('')
      .toUpperCase() || '?'
  );
}

function getClassName(
  size: NonNullable<AvatarGroupProps['size']>,
  overlap: NonNullable<AvatarGroupProps['overlap']>,
  className?: string,
) {
  return [styles.group, styles[size], styles[`overlap${overlap}`], className]
    .filter(Boolean)
    .join(' ');
}

export function AvatarGroup({
  items,
  max = 5,
  size = 'md',
  overlap = 'md',
  className,
}: AvatarGroupProps) {
  if (items.length === 0) {
    return null;
  }

  const visibleCount = Math.max(0, max);
  const visibleItems = items.slice(0, visibleCount);
  const hiddenCount = Math.max(items.length - visibleCount, 0);
  const groupLabel = `Avatar group with ${items.length} ${
    items.length === 1 ? 'person' : 'people'
  }`;

  return (
    <div className={getClassName(size, overlap, className)} aria-label={groupLabel}>
      {visibleItems.map((item) => {
        const initials = item.initials ?? getInitials(item.name);

        return (
          <span
            key={item.id}
            className={styles.avatar}
            {...(!item.src ? { role: 'img', 'aria-label': item.name } : {})}
          >
            {item.src ? (
              <img className={styles.image} src={item.src} alt={item.name} />
            ) : (
              <span className={styles.initials} aria-hidden="true">
                {initials}
              </span>
            )}
          </span>
        );
      })}

      {hiddenCount > 0 ? (
        <span
          className={`${styles.avatar} ${styles.counter}`}
          role="img"
          aria-label={`${hiddenCount} more ${
            hiddenCount === 1 ? 'person' : 'people'
          }`}
        >
          +{hiddenCount}
        </span>
      ) : null}
    </div>
  );
}
