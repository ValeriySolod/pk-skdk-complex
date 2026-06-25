# ПК СКДК — програмний комплекс контролю доставки кореспонденції

Стартова модульна структура програмного комплексу з можливістю додавання нових функціональних блоків.

## Що входить

```text
pk_skdk_complex/
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── api/v1/           # auth, список модулів
│   │   ├── core/             # config, DB, security, module registry
│   │   ├── models/           # SQLAlchemy моделі
│   │   ├── schemas/          # Pydantic DTO
│   │   ├── services/         # audit, workflow
│   │   └── modules/          # функціональні блоки
│   │       ├── organizations/
│   │       ├── registries/
│   │       ├── shipments/
│   │       ├── scanner/
│   │       ├── search/
│   │       ├── reports/
│   │       ├── analytics/
│   │       ├── workflow/
│   │       └── admin/
│   ├── requirements.txt
│   └── .env.example
├── frontend/                 # React + TypeScript + Vite
│   ├── src/app/              # маршрути та registry модулів
│   ├── src/components/       # Layout
│   ├── src/modules/          # frontend-блоки
│   └── .env.example
├── docs/ARCHITECTURE.md
└── docker-compose.yml
```

## Реалізовані базові можливості

- модульна архітектура з `ModuleRegistry`;
- ролі користувачів згідно структури ПК СКДК;
- JWT-авторизація;
- картки організацій, реєстрів і відправлень;
- пошук відправлень за реквізитами;
- сканування штрих-коду з автоматичною зміною статусу;
- аудит створення, редагування та сканування;
- каркас звітів та аналітики;
- React-інтерфейс із меню блоків.

## Запуск backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python -m app.seed
uvicorn app.main:app --reload
```

API буде доступне за адресою:

```text
http://localhost:8000/docs
```

Тестовий користувач після seed:

```text
login: admin
password: admin12345
```

## Запуск frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Frontend буде доступний за адресою:

```text
http://localhost:5173
```

## PostgreSQL через Docker

```bash
docker compose up -d
```

Після цього у `backend/.env` можна використати:

```env
DATABASE_URL=postgresql+psycopg://skdk:skdk@localhost:5432/skdk
```

## Як додати новий блок

Backend:

1. Створити `backend/app/modules/new_block/router.py`.
2. Створити `backend/app/modules/new_block/__init__.py`.
3. Зареєструвати блок через `registry.register(...)`.
4. Додати імпорт у `backend/app/modules_loader.py`.

Frontend:

1. Створити `frontend/src/modules/newBlock/NewBlockPage.tsx`.
2. Додати запис у `frontend/src/app/moduleRegistry.tsx`.

## Важливо

Це стартова архітектура та робочий каркас. Для реальної експлуатації з інформацією обмеженого доступу потрібно окремо реалізувати повний комплекс захисту: сертифіковану автентифікацію, КЕП/ЕЦП, розмежування доступу за підрозділами, журналювання подій безпеки, резервне копіювання, регламенти адміністрування та атестацію середовища.
