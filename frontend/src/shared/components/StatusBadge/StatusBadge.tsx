import css from './StatusBadge.module.css';

interface StatusBadgeProps {
  status: string;
}

const statusLabels: Record<string, string> = {
  created: 'Зареєстровано',
  in_progress: 'В роботі',
  sent: 'Відправлено',
  archived: 'Архів',
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const label = statusLabels[status] ?? status;

  return (
    <span className={`${css.badge} ${css[status] ?? css.default}`}>
      {label}
    </span>
  );
}