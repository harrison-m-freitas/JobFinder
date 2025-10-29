# Diretrizes de Migração
- Sempre `CREATE EXTENSION IF NOT EXISTS pgcrypto;` no inicial.
- Toda alteração **compara tipos** (`compare_type=True` no Alembic).
- Sem `DROP` em produção sem backup e janela.
- Tabelas grandes: criar índice CONCURRENTLY (migração manual).
- Padronizar nomes: `uq_<tabela>_<coluna|...>`, `ix_<tabela>_<coluna>`.
