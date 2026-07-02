import { NavLink, Outlet } from 'react-router-dom';
import { modules } from '../../app/moduleRegistry';
import './layout.css';

export function Layout() {
  return (
    <div className="layout">
      <aside className="sidebar">
        <h1>ПК СКДК</h1>
        <p>Контроль доставки кореспонденції</p>
        <nav>
          <NavLink to="/">Головна</NavLink>
          {modules.map((module) => <NavLink key={module.id} to={module.path}>{module.title}</NavLink>)}
        </nav>
      </aside>
      <main className="content"><Outlet /></main>
    </div>
  );
}
