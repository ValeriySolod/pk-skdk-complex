import { RegistryCard } from './components/RegistryCard';
import css from './RegistriesPage.module.css';
import type { RegistryItem } from './types';

const registryItems: RegistryItem[] = [
  {
    id: 'incoming',
    title: 'Вхідна кореспонденція',
    description: 'Реєстрація отриманих документів, листів та службових матеріалів.',
    path: '/registries/incoming',
    status: 'active',
  },
  {
    id: 'outgoing',
    title: 'Вихідна кореспонденція',
    description: 'Облік документів, що надсилаються організаціям та підрозділам.',
    path: '/registries/outgoing',
    status: 'planned',
  },
  {
    id: 'internal',
    title: 'Внутрішні документи',
    description: 'Реєстр внутрішніх службових документів та доручень.',
    path: '/registries/internal',
    status: 'planned',
  },
  {
    id: 'templates',
    title: 'Шаблони реєстрів',
    description: 'Налаштування шаблонів реєстраційних карток і QR-кодів.',
    path: '/registries/templates',
    status: 'planned',
  },
];

export function RegistriesPage() {
  return (
    <section className={css.page}>
      <div className={css.header}>
        <div>
          <p className={css.eyebrow}>ПК СКДК</p>
          <h2 className={css.title}>Реєстри</h2>
          <p className={css.subtitle}>
            Створення та ведення реєстраційних карток кореспонденції.
          </p>
        </div>
      </div>

      <div className={css.grid}>
        {registryItems.map((item) => (
          <RegistryCard key={item.id} item={item} />
        ))}
      </div>
    </section>
  );
}