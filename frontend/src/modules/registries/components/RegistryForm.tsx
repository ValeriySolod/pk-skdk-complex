import { useState } from 'react';
import { Button } from '../../../shared/components';
import type { CreateRegistryPayload } from '../types';
import css from '../RegistriesPage.module.css';

interface RegistryFormProps {
  onSubmit: (payload: CreateRegistryPayload) => Promise<void>;
}

export function RegistryForm({ onSubmit }: RegistryFormProps) {
  const [number, setNumber] = useState('');
  const [senderOrgId, setSenderOrgId] = useState('1');
  const [qrPayload, setQrPayload] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setIsSubmitting(true);

    try {
      await onSubmit({
        number,
        sender_org_id: Number(senderOrgId),
        qr_payload: qrPayload || null,
      });

      setNumber('');
      setSenderOrgId('1');
      setQrPayload('');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className={css.panelForm} onSubmit={handleSubmit}>
      <label>
        Номер реєстру
        <input
          value={number}
          onChange={(event) => setNumber(event.target.value)}
          placeholder="ВХ-2026-001"
          required
        />
      </label>

      <label>
        ID організації-відправника
        <input
          type="number"
          value={senderOrgId}
          onChange={(event) => setSenderOrgId(event.target.value)}
          required
        />
      </label>

      <label>
        QR payload
        <input
          value={qrPayload}
          onChange={(event) => setQrPayload(event.target.value)}
          placeholder="PK-SKDK:REGISTRY:001"
        />
      </label>

      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Збереження...' : 'Зберегти запис'}
      </Button>
    </form>
  );
}