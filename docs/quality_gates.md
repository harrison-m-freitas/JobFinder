# Quality Gates
- Erro de extração < 5% por fonte (rolling 1h).
- Campos mínimos presentes (> 98%): `title`, `source`, `source_url`, `scraped_at`.
- Freshness diário: ≥ 80% das vagas com `posted_at` ≤ 24h (por fonte/slo).
- Testes ≥ 80% cobertura; contratos validados por Pydantic (Fase 3).
