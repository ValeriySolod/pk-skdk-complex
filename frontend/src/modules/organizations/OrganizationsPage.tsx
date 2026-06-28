import { useEffect, useMemo, useState } from 'react';
import {
  createOrganization,
  deleteOrganization,
  getOrganizations,
  updateOrganization,
} from './api';
import type { Organization, OrganizationCreateData } from './types';
import { Button, Card, EmptyState, Input, Loader, PageHeader, SearchBox } from '../../shared/ui';
import styles from './OrganizationsPage.module.css';

const emptyForm: OrganizationCreateData = {
  name: '',
  edrpou: '',
  address: '',
  responsible_person: '',
  phone: '',
};

export function OrganizationsPage() {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [form, setForm] = useState<OrganizationCreateData>(emptyForm);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  async function loadOrganizations() {
    try {
      setLoading(true);
      setError('');
      const data = await getOrganizations();
      setOrganizations(data);
    } catch {
      setError('Не вдалося завантажити організації');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadOrganizations();
  }, []);

  const filteredOrganizations = useMemo(() => {
    const query = search.trim().toLowerCase();

    if (!query) return organizations;

    return organizations.filter((org) =>
      [org.name, org.edrpou, org.address, org.responsible_person, org.phone]
        .filter(Boolean)
        .some((value) => value!.toLowerCase().includes(query))
    );
  }, [organizations, search]);

  function handleChange(
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  function openCreateForm() {
    setEditingId(null);
    setForm(emptyForm);
    setIsFormOpen(true);
    setError('');
    setSuccess('');
  }

  function handleEdit(org: Organization) {
    setEditingId(org.id);
    setForm({
      name: org.name,
      edrpou: org.edrpou ?? '',
      address: org.address,
      responsible_person: org.responsible_person ?? '',
      phone: org.phone ?? '',
    });
    setIsFormOpen(true);
    setError('');
    setSuccess('');
  }

  function closeForm() {
    setEditingId(null);
    setForm(emptyForm);
    setIsFormOpen(false);
    setError('');
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();

    if (!form.name.trim() || !form.address.trim()) {
      setError('Назва та адреса є обовʼязковими');
      return;
    }

    const payload = {
      ...form,
      edrpou: form.edrpou || null,
      responsible_person: form.responsible_person || null,
      phone: form.phone || null,
    };

    try {
      setError('');
      setSuccess('');

      if (editingId) {
        await updateOrganization(editingId, payload);
        setSuccess('Дані організації оновлено');
      } else {
        await createOrganization(payload);
        setSuccess('Організацію створено');
      }

      closeForm();
      await loadOrganizations();
    } catch {
      setError('Не вдалося зберегти організацію');
    }
  }

  async function handleDelete(id: number) {
    const confirmed = window.confirm('Видалити організацію?');

    if (!confirmed) return;

    try {
      setError('');
      setSuccess('');
      await deleteOrganization(id);
      setSuccess('Організацію видалено');
      await loadOrganizations();
    } catch {
      setError('Не вдалося видалити організацію');
    }
  }

  return (
    <div className={styles.page}>
      <PageHeader
        title="Організації"
        description="Договірна база відправників та юридичних осіб"
        actions={
          <Button type="button" onClick={openCreateForm}>
            Додати організацію
          </Button>
        }
      />

      {success && <div className={styles.success}>{success}</div>}
      {error && <div className={styles.error}>{error}</div>}

      {isFormOpen && (
        <Card className={styles.formCard}>
          <form className={styles.form} onSubmit={handleSubmit}>
            <h2>{editingId ? 'Редагувати організацію' : 'Додати організацію'}</h2>

            <Input label="Назва" name="name" value={form.name} onChange={handleChange} required />

            <Input label="ЄДРПОУ" name="edrpou" value={form.edrpou ?? ''} onChange={handleChange} />

            <label>
              Адреса *
              <textarea name="address" value={form.address} onChange={handleChange} />
            </label>

            <Input
              label="Відповідальна особа"
              name="responsible_person"
              value={form.responsible_person ?? ''}
              onChange={handleChange}
            />

            <Input label="Телефон" name="phone" value={form.phone ?? ''} onChange={handleChange} />

            <div className={styles.actions}>
              <Button type="submit">
                {editingId ? 'Зберегти зміни' : 'Додати'}
              </Button>

              <Button type="button" variant="secondary" onClick={closeForm}>
                Скасувати
              </Button>
            </div>
          </form>
        </Card>
      )}

      <SearchBox
        value={search}
        onChange={setSearch}
        placeholder="Пошук за назвою, ЄДРПОУ, адресою, відповідальною особою..."
      />

      <div className={styles.tableWrap}>
        {loading ? (
          <Loader />
        ) : (
          <table className={styles.table}>
            <thead>
              <tr>
                <th>№</th>
                <th>Назва</th>
                <th>ЄДРПОУ</th>
                <th>Адреса</th>
                <th>Відповідальна особа</th>
                <th>Телефон</th>
                <th>Дії</th>
              </tr>
            </thead>

            <tbody>
              {filteredOrganizations.map((org, index) => (
                <tr key={org.id}>
                  <td>{index + 1}</td>
                  <td>{org.name}</td>
                  <td>{org.edrpou || '—'}</td>
                  <td>{org.address}</td>
                  <td>{org.responsible_person || '—'}</td>
                  <td>{org.phone || '—'}</td>
                  <td className={styles.rowActions}>
                    <Button type="button" onClick={() => handleEdit(org)}>
                      Редагувати
                    </Button>

                    <Button type="button" variant="danger" onClick={() => handleDelete(org.id)}>
                      Видалити
                    </Button>
                  </td>
                </tr>
              ))}

              {filteredOrganizations.length === 0 && (
                <tr>
                  <td colSpan={7}>
                    <EmptyState text="Організацій не знайдено" />
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}