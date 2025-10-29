# Checklist de Revisão (por PR de fonte)
- [ ] `docs/scrapers/<fonte>.md` atualizado
- [ ] robots/ToS verificados e logados
- [ ] Rate limit configurado
- [ ] Amostra HTML/JSON em `tests/fixtures/<fonte>/`
- [ ] Parser cobre paginação/edge-cases
- [ ] Métricas e logs com `source` e `url`
- [ ] Dedupe respeita `(source, external_id)`
- [ ] Testes unitários e de contrato OK
