from __future__ import annotations

import secrets
from collections.abc import Iterable, Sequence
from typing import Final, cast

import scrapy
from scrapy.http import Request

DEFAULT_USER_AGENTS: Final[tuple[str, ...]] = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36",
    # Firefox (desktop)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.0; rv:125.0) Gecko/20100101 Firefox/125.0",
    # Safari (macOS)
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/17.4 Safari/605.1.15",
    # Chrome (Android)
    "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Mobile Safari/537.36",
)


class UserAgentRotationMiddleware:
    def __init__(self, user_agents: Iterable[str] | None = None) -> None:
        self._uas: tuple[str, ...] = self._normalize(user_agents)

    @classmethod
    def from_crawler(cls, crawler: scrapy.crawler.Crawler) -> UserAgentRotationMiddleware:
        raw = crawler.settings.getlist("USER_AGENT_LIST")
        uas = cast(Sequence[str], raw)
        return cls(uas)

    def process_request(self, request: Request, spider: scrapy.Spider) -> None:
        if self._has_user_agent(request):
            return None
        request.headers["User-Agent"] = secrets.choice(self._uas)
        return None

    def _normalize(self, user_agents: Iterable[str] | None) -> tuple[str, ...]:
        candidates = tuple(
            u.strip() for u in (user_agents or DEFAULT_USER_AGENTS) if u and u.strip()
        )
        if candidates:
            return candidates
        return DEFAULT_USER_AGENTS

    def _has_user_agent(self, request: Request) -> bool:
        return bool(request.headers.get(b"User-Agent") or request.headers.get("User-Agent"))
