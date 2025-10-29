# Known Issues (para correção na implementação)
- **`skills.created_at`** no ORM aparece como `String` com default `"now()"`; no banco deve ser `timestamptz`. Ajustar modelo e migração.
- Validar `server_default=func.now()` uniformemente para `created_at/updated_at`.
- Confirmar tamanhos de colunas (`source_url` 1024) e adicionar validação na API.
