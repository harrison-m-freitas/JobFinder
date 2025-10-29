# ADR-0001 — Banco: PostgreSQL 16
## Status
Aprovado

## Contexto
Necessidade de JSONB, índices eficientes e facilidade de operacionalização.

## Decisão
PostgreSQL 16 como fonte única de verdade, com Alembic para versionamento.

## Consequências
- Simplicidade operacional e SQL padrão.
- JSONB para `tags/extra`.
- Cuidado com migrações atômicas e bloqueios (janelas fora de pico).
