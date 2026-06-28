# Frontend Architecture

## Stack

- React
- TypeScript
- Vite
- React Router
- Axios

## Structure

`frontend/src/app` — application entry configuration and module registry.

`frontend/src/pages` — top-level pages such as login.

`frontend/src/modules` — business modules.

`frontend/src/shared` — reusable infrastructure, UI, API clients, config and shared types.

## Rules

- Do not duplicate reusable UI inside modules.
- Module-specific components stay inside the module.
- Universal components go to `shared/ui`.
- API calls are isolated from UI components.
- After each task, `npm run build` must pass.