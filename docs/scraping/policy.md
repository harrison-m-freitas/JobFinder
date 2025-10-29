# Política de Scraping (Obrigatória)
1. **Verificar robots.txt** (runtime) e cachear decisão por 24h.
2. **ToS**: ler/registrar pontos-chave; se restritiva → **não executar** scraper real (usar blueprint/mock).
3. **Rate limit**: default 1 rps/fonte; ajustar por fonte.
4. **Identificação**: `User-Agent` claro com contato (ex.: `JobHunterBot/0.1 (+contact@example.com)`).
5. **Retry/backoff**: 429/5xx → backoff exponencial com jitter, máximo 5 tentativas.
6. **Cache HTTP**: usar ETag/Last-Modified; condicional GET.
7. **Respeito ao site**: sem contornar anti-bot/captcha; sem login; sem payloads pesados.
8. **Stop rules**: 403/anti-bot → parar fonte, registrar métrica e abrir ticket.
