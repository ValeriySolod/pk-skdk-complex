import { Link } from 'react-router-dom';
import css from '../RegistriesPage.module.css';
import type { RegistryItem } from '../types';

interface RegistryCardProps {
  item: RegistryItem;
}

export function RegistryCard({ item }: RegistryCardProps) {
  return (
    <Link to={item.path} className={css.card}>
      <div className={css.cardHeader}>
        <h3 className={css.cardTitle}>{item.title}</h3>
        <span className={css.badge}>
          {item.status === 'active' ? 'Активний' : 'Планується'}
        </span>
      </div>

      <p className={css.cardText}>{item.description}</p>
    </Link>
  );
}