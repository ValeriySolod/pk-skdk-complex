import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { createRegistry, fetchRegistries } from '../api/registries';
import { RegistryForm } from '../components/RegistryForm';
import { RegistryTable } from '../components/RegistryTable';
import type { CreateRegistryPayload, RegistryRecord } from '../types';
import css from '../RegistriesPage.module.css';

export function IncomingRegistryPage() {
  const [items, setItems] = useState<RegistryRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isPanelOpen, setIsPanelOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [error, setError] = useState('');

  async function loadRegistries() {
    try {
      setError('');
      setIsLoading(true);

      const data = await fetchRegistries();
      setItems(data);
    } catch {
      setError('Не вдалося завантажити реєстр.');
    } finally {
      setIsLoading(false);
    }
  }

  async function handleCreate(payload: CreateRegistryPayload) {
    const created = await createRegistry(payload);

    setItems((prevItems) => [created, ...prevItems]);
    setIsPanelOpen(false);
  }

  const filteredItems = useMemo(() => {
    const normalizedQuery = searchQuery.trim().toLowerCase();

    if (!normalizedQuery) {
      return items;
    }

    return items.filter((item) => {
      return (
        item.number.toLowerCase().includes(normalizedQuery) ||
        String(item.sender_org_id).includes(normalizedQuery) ||
        item.status.toLowerCase().includes(normalizedQuery) ||
        (item.qr_payload ?? '').toLowerCase().includes(normalizedQuery)
      );
    });
  }, [items, searchQuery]);

  useEffect(() => {
    loadRegistries();
  }, []);

  return (
    <section className={css.page}>
      <div className={css.header}>
        <div>
          <p className={css.eyebrow}>Реєстри</p>
          <h2 className={css.title}>Вхідна кореспонденція</h2>
          <p className={css.subtitle}>
            Облік отриманих реєстрів кореспонденції з QR-кодами.
          </p>
        </div>
      </div>

      <div className={css.toolbar}>
        <Link to="/registries" className={css.secondaryButton}>
          ← До реєстрів
        </Link>

        <input
          className={css.searchInput}
          value={searchQuery}
          onChange={(event) => setSearchQuery(event.target.value)}
          placeholder="Пошук за номером, статусом або QR..."
        />

        <button
          type="button"
          className={css.primaryButton}
          onClick={() => setIsPanelOpen(true)}
        >
          + Новий запис
        </button>
      </div>

      {isLoading && <p>Завантаження...</p>}

      {error && <p className={css.error}>{error}</p>}

      {!isLoading && !error && <RegistryTable items={filteredItems} />}

      {isPanelOpen && (
        <div className={css.panelOverlay}>
          <aside className={css.sidePanel}>
            <div className={css.panelHeader}>
              <div>
                <p className={css.eyebrow}>Новий запис</p>
                <h3 className={css.panelTitle}>Вхідна кореспонденція</h3>
              </div>

              <button
                type="button"
                className={css.closeButton}
                onClick={() => setIsPanelOpen(false)}
              >
                ×
              </button>
            </div>

            <RegistryForm onSubmit={handleCreate} />
          </aside>
        </div>
      )}
    </section>
  );
}