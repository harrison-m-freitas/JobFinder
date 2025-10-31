# src/job_finder/scraping/middlewares/ban_detection.py
from __future__ import annotations

from collections import defaultdict
from typing import Any, Final, cast

import scrapy
from scrapy.http import Request, Response
from twisted.internet import reactor as _reactor

from job_finder.obs import metrics as m

reactor = cast(Any, _reactor)


class BanDetectionMiddleware:
    BAD_STATUSES: Final[frozenset[int]] = frozenset({403, 429})

    def __init__(self, threshold: int = 3, sleep_seconds: int = 60) -> None:
        self.threshold = threshold
        self.sleep_seconds = sleep_seconds
        self._streak: dict[str, int] = defaultdict(int)
        self._is_paused: bool = False

    @classmethod
    def from_crawler(cls, crawler: scrapy.crawler.Crawler) -> BanDetectionMiddleware:
        th = int(crawler.settings.getint("BAN_THRESHOLD", 3))
        sl = int(crawler.settings.getint("BAN_SLEEP_SECONDS", 60))
        return cls(threshold=th, sleep_seconds=sl)

    def _slot_key(self, request: Request) -> str:
        meta_slot = request.meta.get("download_slot")
        if isinstance(meta_slot, str) and meta_slot:
            return meta_slot

        url = str(request.url)
        parts = url.split("/")
        if len(parts) > 2 and parts[2]:
            return parts[2]
        return url

    def process_response(
        self, request: Request, response: Response, spider: scrapy.Spider
    ) -> Response:
        slot = self._slot_key(request)
        self._update_streak(slot, response.status)

        if self._should_pause(slot):
            self._pause_engine(slot, spider)
        return response

    def _update_streak(self, slot: str, status: int) -> None:
        if status in self.BAD_STATUSES:
            self._streak[slot] += 1
            return
        self._streak[slot] = 0

    def _should_pause(self, slot: str) -> bool:
        if self._is_paused:
            return False
        return self._streak[slot] >= self.threshold

    def _pause_engine(self, slot: str, spider: scrapy.Spider) -> None:
        self._emit_ban(slot, spider)
        self._is_paused = True
        self._streak[slot] = 0

        engine = getattr(spider.crawler, "engine", None)
        if engine is None:
            self._resume_immediately(slot, spider)
            return

        try:
            engine.pause()
        except Exception:
            self._resume_immediately(slot, spider)
            return

        reactor.callLater(self.sleep_seconds, self._resume, spider, slot)

    def _emit_ban(self, slot: str, spider: scrapy.Spider) -> None:
        m.SCRAPY_BANS.labels(spider=spider.name, slot=slot).inc()
        m.SCRAPY_BAN_PAUSED.labels(spider=spider.name, slot=slot).set(1)

    def _resume_immediately(self, slot: str, spider: scrapy.Spider) -> None:
        self._is_paused = False
        m.SCRAPY_BAN_PAUSED.labels(spider=spider.name, slot=slot).set(0)

    def _resume(self, spider: scrapy.Spider, slot: str) -> None:
        try:
            engine = getattr(spider.crawler, "engine", None)
            if engine is not None:
                engine.unpause()
        finally:
            self._resume_immediately(slot, spider)
