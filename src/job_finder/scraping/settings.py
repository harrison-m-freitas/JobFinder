from __future__ import annotations

import os
from typing import Final

BOT_NAME = "jobhunter"

SPIDER_MODULES = ["job_finder.scraping.spiders"]
NEWSPIDER_MODULE = "job_finder.scraping.spiders"

# Compliance (permite controlar por ENV; default: desligado)
ROBOTSTXT_OBEY = os.getenv("SCRAPY_OBEY_ROBOTS", "0") == "1"

# Valores default sensatos, mas todos parametrizáveis via env
CONCURRENT_REQUESTS = int(os.getenv("SCRAPY_CONCURRENT_REQUESTS", "8"))
CONCURRENT_REQUESTS_PER_DOMAIN = int(os.getenv("SCRAPY_CONCURRENT_PER_DOMAIN", "4"))
DOWNLOAD_DELAY = float(os.getenv("SCRAPY_DOWNLOAD_DELAY", "1.0"))
RANDOMIZE_DOWNLOAD_DELAY = True

# AutoThrottle regula dinamicamente o delay por slot/domínio
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = float(os.getenv("SCRAPY_AUTOTHROTTLE_START_DELAY", "0.5"))
AUTOTHROTTLE_MAX_DELAY = float(os.getenv("SCRAPY_AUTOTHROTTLE_MAX_DELAY", "10.0"))
AUTOTHROTTLE_TARGET_CONCURRENCY = float(os.getenv("SCRAPY_AUTOTHROTTLE_TGT_CONC", "2.0"))
AUTOTHROTTLE_DEBUG = False

# HTTP Cache (condicional)
HTTPCACHE_ENABLED = True
HTTPCACHE_POLICY = "scrapy.extensions.httpcache.RFC2616Policy"
HTTPCACHE_EXPIRATION_SECS = int(os.getenv("SCRAPY_HTTPCACHE_TTL", "14400"))  # 4h por padrão
HTTPCACHE_GZIP = True
HTTPCACHE_DIR = os.getenv("SCRAPY_HTTPCACHE_DIR", ".scrapy/httpcache")

# Logs estruturados
LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
LOG_LEVEL = "INFO"

DOWNLOADER_MIDDLEWARES = {
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
    "job_finder.scraping.middlewares.user_agent.UserAgentRotationMiddleware": 400,
    "job_finder.scraping.middlewares.policy.PolicyMiddleware": 543,
    "job_finder.scraping.middlewares.proxy_rotation.ProxyRotationMiddleware": 560,
    "job_finder.scraping.middlewares.ban_detection.BanDetectionMiddleware": 570,
}

# ===== Retry com backoff exponencial (3.5) =====
RETRY_ENABLED = True
RETRY_TIMES = int(os.getenv("SCRAPY_RETRY_TIMES", "3"))
# Retries para erros transitórios comuns (inclui 429/503 etc.)
RETRY_HTTP_CODES = [429, 500, 502, 503, 504, 522, 524, 408]
# Backoff exponencial (se a sua versão do Scrapy não suportar, é ignorado sem quebrar)
RETRY_BACKOFF_BASE = float(os.getenv("SCRAPY_RETRY_BACKOFF_BASE", "2"))
RETRY_BACKOFF_MAX = float(os.getenv("SCRAPY_RETRY_BACKOFF_MAX", "60"))

# Opcional: priorizar retries (mantém filas vivas para novas URLs)
RETRY_PRIORITY_ADJUST = -1

ITEM_PIPELINES = {
    "job_finder.scraping.pipelines.dedupe_pipeline.DedupePipeline": 200,
    "job_finder.scraping.pipelines.db_pipeline.DbPipeline": 300,
}

# Custom user agents (opcional)
USER_AGENT_LIST: Final[tuple[str, ...]] = ()


# Proxy rotation
# Exemplos de entrada: "http://user:pass@host:port", "socks5://host:1080"
PROXY_LIST: Final[tuple[str, ...]] = (
    tuple(os.getenv("SCRAPY_PROXIES", "").split()) if os.getenv("SCRAPY_PROXIES") else ()
)
PROXY_LIST_FILE = os.getenv("SCRAPY_PROXIES_FILE")  # caminho opcional de arquivo com proxies

# Estado/dupefilter persistente entre runs — recomendado por spider:
# use: SCRAPY_JOBDIR=.scrapy/jobs/<spider>
JOBDIR = os.getenv("SCRAPY_JOBDIR")
