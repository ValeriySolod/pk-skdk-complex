# Backend Architecture

## Stack

- FastAPI
- SQLAlchemy
- PostgreSQL

## Planned layers

Router → Service → Repository → Database

## Rules

- Routers handle HTTP only.
- Services contain business logic.
- Repositories work with database queries.
- Models describe database structure.
- Schemas describe request and response DTOs.
- Backend changes must be tested before merge.