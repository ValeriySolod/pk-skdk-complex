import { useState } from 'react';
import { Input } from '../../shared/ui';
import { api } from '../../shared/api/client';
import type { Shipment } from '../../shared/types/domain';

export function ScannerPage() {
  const [barcode, setBarcode] = useState('');
  const [result, setResult] = useState<Shipment | null>(null);
  const [error, setError] = useState('');

  async function scan() {
    setError('');
    try {
      const res = await api.post<Shipment>('/scanner/barcode', { barcode });
      setResult(res.data);
    } catch {
      setResult(null);
      setError('Картку не знайдено або перехід статусу неможливий');
    }
  }

  return (
    <section className="panel">
      <h2>Пошук за штрих/QR-кодом</h2>
      <p>Після сканування система знаходить картку і переводить її на наступний технологічний етап.</p>
      <Input value={barcode} onChange={(e) => setBarcode(e.target.value)} placeholder="PKSKDK-000001" /> <button onClick={scan}>Сканувати</button>
      {error && <p>{error}</p>}
      {result && <div className="card"><b>{result.barcode}</b><p>{result.recipient_name}</p><p>Статус: {result.status}</p></div>}
    </section>
  );
}
