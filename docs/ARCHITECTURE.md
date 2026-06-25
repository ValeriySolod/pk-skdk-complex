# Архітектура ПК СКДК

## Призначення
ПК СКДК побудовано як модульний web-комплекс для автоматизації приймання, обробки, контролю доставки, пошуку, звітності та адміністрування кореспонденції з обмеженням доступу.

## Рівні системи

1. **Frontend** — React/Vite інтерфейс з головним меню, рубрикаторами та окремими модулями.
2. **Backend API** — FastAPI з модульною реєстрацією блоків через `ModuleRegistry`.
3. **Database** — PostgreSQL або SQLite для локального запуску.
4. **Audit** — журнал дій користувачів.
5. **Workflow** — керування переходами станів відправлення.
6. **Reports** — статистичні та карткові звіти.

## Базові блоки

- Організації
- Договори
- Реєстри
- Відправлення
- Сканування штрих/QR-коду
- Пошук
- Звіти
- Аналітика
- Технологічний процес
- Адміністрування

## Як додати новий backend-блок

1. Створити папку `backend/app/modules/<module_name>`.
2. Додати `router.py` з FastAPI endpoint-ами.
3. Додати `__init__.py` з реєстрацією:

```python
from app.core.module_registry import ModuleManifest, registry
from .router import router

def get_router():
    return router

registry.register(ModuleManifest(
    code='new_module',
    title='Новий блок',
    description='Опис блоку',
    router_factory=get_router,
    permissions=['new_module:read'],
))
```

4. Додати імпорт у `backend/app/modules_loader.py`.

## Як додати новий frontend-блок

1. Створити папку `frontend/src/modules/<module_name>`.
2. Додати компонент сторінки.
3. Додати запис у `frontend/src/app/moduleRegistry.tsx`.

## Стани відправлення

- `registered` — зареєстровано
- `accepted` — прийнято
- `transit` — транзит
- `in_delivery` — у доставці
- `delivered` — доставлено
- `archived` — архівовано

## Безпека

Цей стартовий комплекс містить каркас RBAC, JWT-авторизацію та аудит. Для промислової експлуатації необхідно додати сертифіковані засоби захисту інформації, політики доступу до даних за підрозділами, криптографічний захист, резервне копіювання, журналювання подій безпеки та процедури адміністрування.
