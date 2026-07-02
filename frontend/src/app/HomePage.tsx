import { hasModuleNavigation, isModuleVisibleForRole, modules } from './moduleRegistry';

export type HomePageProps = {
  userRole: string;
};

export function HomePage({ userRole }: HomePageProps) {
  const navigationModules = modules
    .filter(hasModuleNavigation)
    .filter((module) => isModuleVisibleForRole(module, userRole))
    .sort((firstModule, secondModule) => {
      return firstModule.navigation.order - secondModule.navigation.order;
    });

  return (
    <>
      <section className="panel">
        <h2>Головне вікно</h2>
        <p>Єдиний інформаційний простір для карток, реєстрів, описів, маршрутних/добових/видаткових відомостей, пошуку, сканування та звітності.</p>
      </section>
      <section className="grid">
        {navigationModules.map((module) => (
          <article className="card" key={module.id}>
            <h3>{module.title}</h3>
            <p>Блок: {module.id}</p>
          </article>
        ))}
      </section>
    </>
  );
}
