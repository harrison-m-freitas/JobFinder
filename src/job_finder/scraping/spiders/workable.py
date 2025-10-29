# src/job_finder/scraping/spiders/workable.py
from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Any

import scrapy
from scrapy.http import Request, Response


class WorkableSpider(scrapy.Spider):
    name = "workable"
    allowed_domains = ["apply.workable.com"]

    def __init__(self, org: str | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.org = org or "example"

    def start_requests(self) -> Iterable[Request]:
        url = f"https://apply.workable.com/api/v3/accounts/{self.org}/jobs"
        yield scrapy.Request(url, callback=self.parse_api)

    def parse_api(self, response: Response) -> Iterable[dict[str, Any]]:
        try:
            data = json.loads(response.text)
        except Exception:
            data = {}
        for job in data.get("results", []):
            yield {
                "source": self.name,
                "external_id": job.get("shortcode"),
                "source_url": job.get("url") or response.url,
                "title": job.get("title"),
                "company_name": self.org,
                "location": (job.get("location", {}) or {}).get("city"),
                "remote": bool(job.get("workplace", "") in ("remote", "hybrid")),
                "language": "en",
                "tags": {"board": "workable", "org": self.org},
            }
