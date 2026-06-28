import type { ReactNode } from 'react';
import css from './SidePanel.module.css';

interface SidePanelProps {
  title: string;
  eyebrow?: string;
  children: ReactNode;
  onClose: () => void;
}

export function SidePanel({
  title,
  eyebrow,
  children,
  onClose,
}: SidePanelProps) {
  return (
    <div className={css.overlay}>
      <aside className={css.panel}>
        <div className={css.header}>
          <div>
            {eyebrow && <p className={css.eyebrow}>{eyebrow}</p>}
            <h2 className={css.title}>{title}</h2>
          </div>

          <button
            type="button"
            className={css.closeButton}
            onClick={onClose}
            aria-label="Закрити панель"
          >
            ×
          </button>
        </div>

        {children}
      </aside>
    </div>
  );
}