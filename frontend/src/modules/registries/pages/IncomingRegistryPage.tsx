import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, PageHeader, SearchInput, SidePanel } from '../../../shared/components';
import { createRegistry, fetchRegistries } from '../api/registries';
import { RegistryForm } from '../components/RegistryForm';
import { RegistryTable } from '../components/RegistryTable';
import type { CreateRegistryPayload, RegistryRecord } from '../types';
import css from '../RegistriesPage.module.css';

export function IncomingRegistryPage() {
  const navigate = useNavigate();
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
      <PageHeader
        eyebrow="Реєстри"
        title="Вхідна кореспонденція"
        description="Облік отриманих реєстрів кореспонденції з QR-кодами."
      />

      <div className={css.toolbar}>
        <Button variant="secondary" onClick={() => navigate('/registries')}>
          ← До реєстрів
        </Button>

        <SearchInput
          value={searchQuery}
          onChange={(event) => setSearchQuery(event.target.value)}
          placeholder="Пошук за номером, статусом або QR..."
        />

        <Button onClick={() => setIsPanelOpen(true)}>
          + Новий запис
        </Button>
      </div>

      {isLoading && <p>Завантаження...</p>}

      {error && <p className={css.error}>{error}</p>}

      {!isLoading && !error && <RegistryTable items={filteredItems} />}

      {isPanelOpen && (
        <SidePanel
          eyebrow="Новий запис"
          title="Вхідна кореспонденція"
          onClose={() => setIsPanelOpen(false)}
        >
          <RegistryForm onSubmit={handleCreate} />
        </SidePanel>
      )}
    </section>
  );
}
