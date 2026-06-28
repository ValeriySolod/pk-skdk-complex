import type { ReactNode } from 'react';
import css from './PageHeader.module.css';

interface PageHeaderProps {
  eyebrow?: string;
  title: string;
  description?: string;
  actions?: ReactNode;
}

export function PageHeader({
  eyebrow,
  title,
  description,
  actions,
}: PageHeaderProps) {
  return (
    <header className={css.header}>
      <div>
        {eyebrow && <p className={css.eyebrow}>{eyebrow}</p>}
        <h1 className={css.title}>{title}</h1>
        {description && <p className={css.description}>{description}</p>}
      </div>

      {actions && <div className={css.actions}>{actions}</div>}
    </header>
  );
}