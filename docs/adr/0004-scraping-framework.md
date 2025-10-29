# ADR-0004 — Scraping: Scrapy + httpx + Playwright
## Decisão
- Scrapy para crawl/pipelines.
- httpx para chamadas simples (feeds/RSS/APIs).
- Playwright apenas quando necessário (JS-heavy) e **se robots/ToS permitirem**.

## Políticas
- Rate limit por fonte configurável.
- Retry com backoff exponencial + jitter.
- Cache HTTP (ETag/Last-Modified) quando suportado.
