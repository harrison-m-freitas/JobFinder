from __future__ import annotations

import logging
import secrets
from collections import defaultdict
from typing import Final

import scrapy
from scrapy.http import Request, Response

from job_finder.obs import metrics as m

logger = logging.getLogger(__name__)


class ProxyRotationMiddleware:
    # manter em 1 linha para não dar ping-pong entre black e ruff
    BAD_STATUS: Final[frozenset[int]] = frozenset(
        {
            403,
            407,
            408,
            429,
            500,
            502,
            503,
            504,
            522,
            524,
        }
    )

    def __init__(self, proxies: list[str]) -> None:
        self._pool: list[str] = [p.strip() for p in proxies if p and p.strip()]
        self._penalty: dict[str, int] = defaultdict(int)

    @classmethod
    def from_crawler(cls, crawler: scrapy.crawler.Crawler) -> ProxyRotationMiddleware:
        proxies = cls._load_proxies(crawler)
        return cls(proxies)

    def process_request(self, request: Request, spider: scrapy.Spider) -> None:
        current = request.meta.get("proxy")
        if self._should_switch_on_retry(request):
            self._switch_proxy_on_retry(request, spider, current)
            return None
        if current:
            return None
        self._set_proxy(request, self._pick_proxy())
        return None

    def process_response(
        self,
        request: Request,
        response: Response,
        spider: scrapy.Spider,
    ) -> Response:
        if response.status in self.BAD_STATUS:
            self._penalize_proxy(request, spider, f"status_{response.status}")
        return response

    def process_exception(
        self,
        request: Request,
        exception: BaseException,
        spider: scrapy.Spider,
    ) -> Response | None:
        self._penalize_proxy(request, spider, exception.__class__.__name__)
        return None

    @staticmethod
    def _load_proxies(crawler: scrapy.crawler.Crawler) -> list[str]:
        proxies: list[str] = []
        proxies.extend(crawler.settings.getlist("PROXY_LIST"))
        path = crawler.settings.get("PROXY_LIST_FILE")
        if path:
            try:
                with open(path, encoding="utf-8") as fh:
                    proxies.extend([ln.strip() for ln in fh if ln.strip()])
            except FileNotFoundError:
                logger.warning("[proxy] arquivo não encontrado: %s", path)
        return proxies

    def _should_switch_on_retry(self, request: Request) -> bool:
        retry_times = int(request.meta.get("retry_times", 0))
        return retry_times > 0

    def _switch_proxy_on_retry(
        self,
        request: Request,
        spider: scrapy.Spider,
        current: str | None,
    ) -> None:
        new_proxy = self._pick_proxy(exclude=current)
        if new_proxy and new_proxy != current:
            self._set_proxy(request, new_proxy)
            m.SCRAPY_PROXY_SWITCHES.labels(spider=spider.name).inc()
        m.SCRAPY_RETRIES.labels(spider=spider.name, reason="retry_times").inc()

    def _penalize_proxy(self, request: Request, spider: scrapy.Spider, cause: str) -> None:
        proxy = request.meta.get("proxy")
        if not proxy:
            return
        self._penalty[proxy] += 1
        m.SCRAPY_PROXY_PENALTIES.labels(spider=spider.name, cause=cause).inc()

    def _pick_proxy(self, exclude: str | None = None) -> str | None:
        if not self._pool:
            return None
        candidates = [p for p in self._pool if p != exclude]
        if not candidates:
            candidates = self._pool[:]
        best = min(candidates, key=lambda p: self._penalty.get(p, 0))
        tied = [p for p in candidates if self._penalty.get(p, 0) == self._penalty.get(best, 0)]
        return secrets.choice(tied)

    def _set_proxy(self, request: Request, proxy: str | None) -> None:
        if proxy:
            request.meta["proxy"] = proxy
