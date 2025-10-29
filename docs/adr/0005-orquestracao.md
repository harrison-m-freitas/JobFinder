# ADR-0005 — Orquestração: Airflow + Celery
- Airflow para DAGs (priorização, SLAs, retries globais).
- Celery para enriquecimentos assíncronos e tarefas de alto throughput.
- Redis como broker para dev.
