# JobHunter — Data Platform

![CI](https://github.com/harrison-m-freitas/JobFinder/actions/workflows/ci.yml/badge.svg)


**Fases ativas:** Fase 1 (Setup) e Fase 2 (DB/ORM)

## Rodar
```bash
cp .env.example .env
make up
make migrate-up
make test
````

## Estrutura

* `src/db` ORM, sessão e migrações (Alembic)
* `docs/` arquitetura e runbook
* `tests/` testes unitários e de esquema
