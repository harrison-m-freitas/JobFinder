# src/job_finder/scraping/middlewares/policy.py
from __future__ import annotations

import time

import scrapy
import structlog
from scrapy.http import Request, Response

from job_finder.obs import metrics as m

log = structlog.get_logger(__name__)


class PolicyMiddleware:
    def __init__(self) -> None:
        self._t0: dict[int, float] = {}

    def process_request(self, request: Request, spider: scrapy.Spider) -> None:
        self._t0[id(request)] = time.perf_counter()
        m.SCRAPY_REQUESTS.labels(spider=spider.name).inc()
        return None

    def process_response(
        self,
        request: Request,
        response: Response,
        spider: scrapy.Spider,
    ) -> Response:
        latency_ms = self._latency_ms(request)
        self._log_http_response(spider, response, latency_ms)
        self._emit_response_metrics(spider, response, latency_ms)
        self._emit_slot_delay(spider, request)
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

    def _latency_ms(self, request: Request) -> float:
        started_at = self._t0.pop(id(request), time.perf_counter())
        return (time.perf_counter() - started_at) * 1000

    def _log_http_response(
        self,
        spider: scrapy.Spider,
        response: Response,
        latency_ms: float,
    ) -> None:
        log.info(
            "http_response",
            source=getattr(spider, "name", "unknown"),
            url=str(response.url),
            status_code=response.status,
            latency_ms=int(latency_ms),
        )

    def _emit_response_metrics(
        self,
        spider: scrapy.Spider,
        response: Response,
        latency_ms: float,
    ) -> None:
        m.SCRAPY_RESPONSES.labels(
            spider=spider.name,
            status=str(response.status),
        ).inc()
        m.SCRAPY_DOWNLOAD_LATENCY_MS.observe(latency_ms)

    def _emit_slot_delay(self, spider: scrapy.Spider, request: Request) -> None:
        slot_key = self._slot_key(request)
        crawler = getattr(spider, "crawler", None)
        if crawler is None:
            return
        engine = getattr(crawler, "engine", None)
        if engine is None:
            return
        downloader = getattr(engine, "downloader", None)
        if downloader is None:
            return
        slots = getattr(downloader, "slots", None)
        if not slots:
            return
        slot = slots.get(slot_key)
        if slot is None:
            return
        delay = getattr(slot, "delay", None)
        if delay is None:
            return
        m.SCRAPY_SLOT_DELAY.labels(
            spider=spider.name,
            slot=slot_key,
        ).set(float(delay))

    def _slot_key(self, request: Request) -> str:
        slot = request.meta.get("download_slot")
        if isinstance(slot, str) and slot:
            return slot
        url = str(request.url)
        parts = url.split("/")
        if len(parts) > 2 and parts[2]:
            return parts[2]
        return url
