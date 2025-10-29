# Contratos de Dados (Ingest → DB)
## JobIngest (JSON)
```json
{
  "source": "weworkremotely",
  "external_id": "12345",
  "source_url": "https://weworkremotely.com/remote-jobs/12345",
  "title": "Backend Engineer",
  "company": { "name": "Acme Inc" },
  "location": "São Paulo, BR",
  "remote": true,
  "employment_type": "full-time",
  "seniority": "senior",
  "currency": "BRL",
  "salary_min": 15000,
  "salary_max": 20000,
  "tags": { "stack": ["python","aws"] },
  "language": "pt",
  "posted_at": "2025-10-15T00:00:00Z",
  "description_html": "<p>...</p>"
}
```


### Regras

* Campos não inferíveis → `null`, nunca inventar.
* `external_id` obrigatório **se** disponível de forma estável; senão derive um hash estável do `source_url`.
* `company.name` é o mínimo para vincular/CRIAR empresa.
