import { modules } from './moduleRegistry';

export function HomePage() {
  return (
    <>
      <section className="panel">
        <h2>Головне вікно</h2>
        <p>Єдиний інформаційний простір для карток, реєстрів, описів, маршрутних/добових/видаткових відомостей, пошуку, сканування та звітності.</p>
      </section>
      <section className="grid">
        {modules.map((module) => <article className="card" key={module.code}><h3>{module.title}</h3><p>Блок: {module.code}</p></article>)}
      </section>
    </>
  );
}
