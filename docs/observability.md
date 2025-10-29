# Observabilidade
## Logs (JSON)
Campos mínimos: `ts`, `level`, `source`, `url`, `action`, `latency_ms`, `status_code`, `retries`, `policy_decision`, `error_type`, `correlation_id`.

## Métricas
- `scrape_requests_total{source}` (counter)
- `scrape_errors_total{source,type}` (counter)
- `scrape_latency_ms{source}` (histogram)
- `robots_disallowed_total{source}` (counter)
- `dedupe_hits_total` (counter)
- `nlp_extract_skills_total` (counter)

## Alertas (exemplos)
- Erro ≥5% por 10 min em uma fonte → alerta.
- Freshness mediana > 48h em fontes “diárias” → alerta.
-
