from __future__ import annotations

BOT_NAME = "jobhunter"

SPIDER_MODULES = ["job_finder.scraping.spiders"]
NEWSPIDER_MODULE = "job_finder.scraping.spiders"

# Compliance
ROBOTSTXT_OBEY = True
USER_AGENT = "JobHunterBot/0.1 (+contact@example.com)"  # Change this to fake User-Agent to bypass restrictions
DOWNLOAD_DELAY = 1.0
CONCURRENT_REQUESTS_PER_DOMAIN = 4
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1.0
AUTOTHROTTLE_MAX_DELAY = 10.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0

# HTTP Cache (condicional)
HTTPCACHE_ENABLED = True
HTTPCACHE_POLICY = "scrapy.extensions.httpcache.RFC2616Policy"
HTTPCACHE_EXPIRATION_SECS = 3600

# Logs estruturados
LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
LOG_LEVEL = "INFO"

DOWNLOADER_MIDDLEWARES = {
    "job_finder.scraping.middlewares.PolicyMiddleware": 543,
}

ITEM_PIPELINES = {
    "job_finder.scraping.pipelines.db_pipeline.DbPipeline": 300,
}
