# src/job_finder/scraping/middlewares.py
from __future__ import annotations

import time

import scrapy
import structlog
from scrapy.http import Request, Response

log = structlog.get_logger(__name__)


class PolicyMiddleware:
    """Registra métricas/decisões básicas (latência, status, robots já é obedecido pelo Scrapy)."""

    def __init__(self) -> None:
        self._t0: dict[int, float] = {}

    def process_request(self, request: Request, spider: scrapy.Spider) -> None:
        self._t0[id(request)] = time.perf_counter()
        return None

    def process_response(
        self, request: Request, response: Response, spider: scrapy.Spider
    ) -> Response:
        t0 = self._t0.pop(id(request), time.perf_counter())
        latency = (time.perf_counter() - t0) * 1000
        log.info(
            "http_response",
            source=getattr(spider, "name", "unknown"),
            url=str(response.url),
            status_code=response.status,
            latency_ms=int(latency),
        )
        return response

    def process_exception(
        self, request: Request, exception: BaseException, spider: scrapy.Spider
    ) -> Response | None:
        log.error(
            "http_exception",
            source=getattr(spider, "name", "unknown"),
            url=str(request.url),
            error_type=exception.__class__.__name__,
        )
        return None
