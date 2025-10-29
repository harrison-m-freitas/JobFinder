# Arquitetura — Visão Geral

> Objetivo: coletar, enriquecer e servir vagas de tecnologia com **robustez**, **conformidade** e **observabilidade**.

## Princípios & NFRs
- **Compliance-first:** obedecer `robots.txt`/ToS; sem login, sem burlar captcha/anti-bot; parar mediante sinais de bloqueio.
- **Confiabilidade:** idempotência, dedupe `(source, external_id)`, retries com backoff + circuit breaker; SLOs por fonte.
- **Escalabilidade:** paralelismo controlado, rate limit adaptativo por fonte, cache HTTP (ETag/Last-Modified).
- **Qualidade de dados:** contratos de dados, campos mínimos, validação e métricas de erro.
- **Observabilidade:** logs estruturados, métricas Prometheus, alertas com error budget.
- **DX:** 12-factor, configs via `.env`, Make/CI, docs por fonte.

## Visão Macro (Containers)
```mermaid
flowchart LR
  %% Correção: substituir "\n" por "<br/>" em rótulos multilinha.
  subgraph External[Internet / Sites de Vagas]
    Sites["Fontes (HTML/RSS/API/ATS)"]
  end

  subgraph Ingestion[Ingestion]
    P0[Source Registry]
    P1["Scrapers (Scrapy/httpx)<br/>+ Playwright (quando necessário)"]
    P2["Policy Engine<br/>robots/ToS • rate-limit • UA/proxy • cache • retries"]
  end

  subgraph Storage[Storage]
    PG[(PostgreSQL 16)]
  end

  subgraph Processing[Processing]
    Dedupe["Dedupe (source, external_id)<br/>+ heurísticas (Fase 3)"]
    E1["Enrichment (NLP/Rules)<br/>skills • seniority • salary"]
  end

  subgraph Orchestration[Orchestration]
    AF[[Airflow DAGs]]
    Q[[Celery/Redis]]
  end

  subgraph Serve[Serve]
    API["FastAPI (consulta/analytics)"]
    Obs[Grafana/Prometheus]
  end

  Sites -->|HTTP| P1
  P0 --> P1 --> P2 --> PG
  PG --> Dedupe --> E1 --> PG
  AF --> P1
  Q --> E1
  PG --> API
  PG --> Obs
```

## Fluxo de Dados (Sequência)

```mermaid
sequenceDiagram
  participant S as Scheduler (Airflow)
  participant C as Scraper
  participant R as Policy Engine (robots/ToS)
  participant H as HTTP/Cache
  participant V as Validação (Contratos)
  participant DB as PostgreSQL
  participant M as Métricas/Logs

  S->>C: Dispara tarefa da fonte F (args: página, janela)
  C->>R: Verifica robots.txt + ToS (decisão cacheada)
  R-->>C: allow | disallow | throttle
  alt disallow
    C->>M: registra robots_disallowed_total++
    C-->>S: encerra com "skipped"
  else allow/throttle
    C->>H: GET condicional (ETag/If-Modified-Since)
    H-->>C: 200 | 304 | 4xx | 5xx
    C->>M: scrape_requests_total++, latency_ms
    alt 200
      C->>V: parse + valida JobIngest
      V-->>C: válido (ou campos nulos justificados)
      C->>DB: UPSERT jobs (ON CONFLICT on (source, external_id))
      DB-->>C: OK
      C->>M: dedupe_hits_total (se aplicável)
    else 304
      C->>M: cache_hit++
    else 429/5xx
      C->>C: retry com backoff + jitter
      C->>M: scrape_errors_total{type="server"}++
    else 403/anti-bot
      C->>M: error_type="antibot" & abre circuito para fonte
    end
  end
```
## Componentes & Responsabilidades

* **Source Registry:** catálogo versionado das fontes (método: HTML/RSS/API/ATS; SLOs; risco; política).
* **Scraper Runtime:** Scrapy (crawl/pipelines) + httpx; Playwright apenas se necessário e permitido.
* **Policy Engine:** checagem de robots/ToS; rate limit dinâmico; user-agent/proxy rotation; stop rules.
* **HTTP Layer:** timeouts, retries/backoff, cache condicional; circuit breaker por domínio.
* **Storage (PostgreSQL):** esquema canônico; índices em `posted_at`/`scraped_at`; JSONB para `tags`.
* **Dedupe:** constraint (source, external_id) + heurísticas futuras (Levenshtein ±2d).
* **Enrichment:** extração de skills/senioridade/salário com regras/NLP; jobs de pós-processamento via Celery.
* **API (FastAPI):** filtros (keyword, seniority, location, remote, salary, company) e agregações (top-N skills, tendências).
* **Observability:** logs JSON, métricas Prometheus, dashboards e alertas (erro/freshness/latência).

## Fronteiras de Confiança & Compliance

* **Internet ↔ Ingestion:** respeitar `robots.txt`/ToS; sem login/captcha bypass; limitar RPS; honrar `Retry-After`.
* **Ingestion ↔ Storage:** upserts idempotentes; transações curtas; schemas versionados (Alembic).
* **Serve ↔ Consumidores:** sanitização/escape do HTML; rate limit de API; paginação e filtros seguros.
* **LGPD:** sem PII de candidatos; dados somente públicos; logs com IP ofuscado/rotação de 30 dias.

## Escalabilidade & Resiliência

* **Capacidade alvo (MVP):** ≥10k vagas/dia; janela de coleta < 2h.
* **Paralelismo:** por domínio (N) e global (G) com “crawl budget” por fonte.
* **Backpressure:** reduzir paralelismo e aumentar intervalo sob erro ≥5%/10 min.
* **Idempotência:** UPSERT por (source, external_id); retriable sem duplicar.
* **Falhas parciais:** circuit breaker por fonte; fila de retry tardio (Celery beat).

## Qualidade de Dados & Contratos

* **Campos mínimos:** `title`, `source`, `source_url`, `scraped_at`.
* **Moeda/Idioma:** ISO 4217/639-1.
* **Contratos (Pydantic):** validações de tipos/intervalos; campos não inferíveis → `null` + log.

## Observabilidade (Métricas & Alertas)

* `scrape_requests_total`, `scrape_errors_total{type}`, `scrape_latency_ms`, `robots_disallowed_total`, `dedupe_hits_total`.
* **Alertas exemplos:** erro ≥5%/10 min; freshness mediana >48h em fontes diárias; p95 latência >3s.

## Segurança

* Segredos via `.env`/secret manager.
* Dependência monitorada (dependabot/safety).
* Sanitização/escape ao servir HTML.

## Itens Abertos / Known Issues

* `skills.created_at` deve ser `timestamptz` (corrigir ORM + migração).
* Validar tamanhos máximos (`source_url` até 1024) na API.
