from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram

# ====== Métricas de Scrapy ======
SCRAPY_REQUESTS = Counter(
    "scrapy_requests_total", "Total de requests emitidos pelo Scrapy", ["spider"]
)
SCRAPY_RESPONSES = Counter(
    "scrapy_responses_total", "Total de responses recebidos pelo Scrapy", ["spider", "status"]
)
SCRAPY_DOWNLOAD_LATENCY_MS = Histogram(
    "scrapy_download_latency_ms",
    "Latência (ms) de downloads HTTP no Scrapy",
    buckets=(10, 25, 50, 100, 250, 500, 1000, 2000, 5000),
)
SCRAPY_RETRIES = Counter(
    "scrapy_retries_total", "Total de tentativas de retry no Scrapy", ["spider", "reason"]
)
SCRAPY_PROXY_SWITCHES = Counter(
    "scrapy_proxy_switches_total", "Trocas de proxy ao realizar retry", ["spider"]
)
SCRAPY_PROXY_PENALTIES = Counter(
    "scrapy_proxy_penalties_total", "Penalidades de proxy por falha/status", ["spider", "cause"]
)
SCRAPY_SLOT_DELAY = Gauge(
    "scrapy_slot_delay_seconds", "Delay atual do downloader slot (AutoThrottle)", ["spider", "slot"]
)
SCRAPY_BANS = Counter(
    "scrapy_bans_total", "Sequências de ban detectadas (403/429)", ["spider", "slot"]
)
SCRAPY_BAN_PAUSED = Gauge(
    "scrapy_ban_paused", "Spider pausada por ban (1=sim,0=não)", ["spider", "slot"]
)
