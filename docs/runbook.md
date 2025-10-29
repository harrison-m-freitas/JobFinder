# Runbook

## Provisionamento local
1. `cp .env.example .env`
2. `make up`
3. `make migrate-up` (idempotente)
4. `make test`

## Operações comuns
- Nova migração: `make migrate-new name=<slug>`
- Atualizar deps: edite `pyproject.toml` e `docker compose up -d --build`
- Logs: `make logs` | Shell: `make shell`
-
## Troubleshooting
- **Conn recusada**: aguarde healthcheck do Postgres; `make logs`
- **Alembic**: conflitos → gere nova migração consolidando alterações
- **Erros de tipagem**: `make format && make type`

## Incidentes de scraping
1) Ver erro/alerta → 2) Checar robots/ToS → 3) Reduzir taxa → 4) Abrir issue → 5) Pausar fonte se necessário.
