# Dedupe
- Chave natural: `(source, external_id)` em `jobs`.
- Heurística (fallback): `lower(title)+company+posted_at±2d` com distância de Levenshtein (Fase 3).
- Dedupe executado pós-ingestão; registrar `dedupe_hits_total`.
