# ADR-0002 — ORM: SQLAlchemy 2.x
## Decisão
SQLAlchemy 2.x (Declarative) + SessionLocal; tipagem estática e testabilidade.

## Consequência
Modelos coesos, migrações orientadas por Alembic; evitar lógica de negócio pesada no ORM.
