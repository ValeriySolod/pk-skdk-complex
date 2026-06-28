import css from './StatusBadge.module.css';

const statusLabels = {
  active: 'Активний',
  planned: 'Планується',
  created: 'Зареєстровано',
  in_progress: 'В роботі',
  sent: 'Відправлено',
  archived: 'Архів',
} as const;

export type KnownStatus = keyof typeof statusLabels;

interface StatusBadgeProps {
  status: KnownStatus | (string & {});
}

function isKnownStatus(status: string): status is KnownStatus {
  return status in statusLabels;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const label = isKnownStatus(status) ? statusLabels[status] : status;
  const statusClass = isKnownStatus(status) ? css[status] : css.default;

  return (
    <span className={`${css.badge} ${statusClass}`}>
      {label}
    </span>
  );
}
