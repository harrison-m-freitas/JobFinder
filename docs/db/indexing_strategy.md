# Estratégia de Índices
- `jobs(posted_at)`, `jobs(scraped_at)` para freshness.
- Buscar por empresa: `jobs(company_id)` index implícito via FK.
- Filtros de API: `jobs(remote)`, `jobs(location)` → avaliar índices parciais depois de perf real.
