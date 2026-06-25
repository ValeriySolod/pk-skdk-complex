import { useState } from 'react';
import { api } from '../../shared/api/client';
import type { Shipment } from '../../shared/types/domain';

export function SearchPage() {
  const [text, setText] = useState('');
  const [rows, setRows] = useState<Shipment[]>([]);
  async function search() {
    const res = await api.get<Shipment[]>('/search/shipments', { params: { text } });
    setRows(res.data);
  }
  return (
    <section className="panel">
      <h2>Пошук</h2>
      <p>Пошук за реквізитами картки, контекстом, областю, районом, грифом та штрих-кодом.</p>
      <input value={text} onChange={(e) => setText(e.target.value)} placeholder="Номер документа / отримувач" /> <button onClick={search}>Знайти</button>
      <table><tbody>{rows.map((row) => <tr key={row.id}><td>{row.barcode}</td><td>{row.recipient_name}</td><td>{row.status}</td></tr>)}</tbody></table>
    </section>
  );
}
