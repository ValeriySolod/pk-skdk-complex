import { useEffect, useState } from 'react';
import { api } from '../../shared/api/client';
import type { Shipment } from '../../shared/types/domain';

export function ShipmentsPage() {
  const [shipments, setShipments] = useState<Shipment[]>([]);

  useEffect(() => {
    api.get<Shipment[]>('/shipments').then((res) => setShipments(res.data)).catch(() => setShipments([]));
  }, []);

  return (
    <section className="panel">
      <h2>Відправлення</h2>
      <p>Картки опису відправлень, статуси доставки, гриф доступу, область та район доставки.</p>
      <table>
        <thead><tr><th>Штрих-код</th><th>Отримувач</th><th>Гриф</th><th>Статус</th></tr></thead>
        <tbody>{shipments.map((item) => <tr key={item.id}><td>{item.barcode}</td><td>{item.recipient_name}</td><td>{item.access_mark}</td><td>{item.status}</td></tr>)}</tbody>
      </table>
    </section>
  );
}
