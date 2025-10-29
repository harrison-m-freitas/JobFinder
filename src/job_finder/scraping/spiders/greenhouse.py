from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Any

import scrapy
from scrapy.http import Request, Response


class GreenhouseSpider(scrapy.Spider):
    name = "greenhouse"
    allowed_domains = ["boards.greenhouse.io"]

    def __init__(self, org: str | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.org = org or "example"  # passe -a org=<org>

    def start_requests(self) -> Iterable[Request]:
        url = f"https://boards.greenhouse.io/boards/{self.org}/embed/jobs"
        yield scrapy.Request(url, callback=self.parse_json)

    def parse_json(self, response: Response) -> Iterable[Request | dict[str, Any]]:
        data = response.xpath("//script[contains(., 'GH')]/text()").get() or ""
        if not data:
            api = f"https://boards.greenhouse.io/boards/{self.org}/jobs"
            yield scrapy.Request(api, callback=self.parse_api)
            return
        for job in response.css("section#jobs div.opening"):
            title = job.css("a::text").get()
            link = job.css("a::attr(href)").get()
            dept = job.css("span.department::text").get()
            yield {
                "source": self.name,
                "external_id": link.strip("/").split("/")[-1] if link else None,
                "source_url": response.urljoin(link) if link else response.url,
                "title": title,
                "company_name": self.org,
                "posted_at": None,
                "remote": "remote" in (dept or "").lower(),
                "language": "en",
                "tags": {"board": "greenhouse", "org": self.org},
            }

    def parse_api(self, response: Response) -> Iterable[dict[str, Any]]:
        try:
            data = json.loads(response.text)
        except Exception:
            data = {}
        for job in data.get("jobs", []):
            yield {
                "source": self.name,
                "external_id": str(job.get("id")),
                "source_url": job.get("absolute_url") or response.url,
                "title": job.get("title"),
                "company_name": self.org,
                "posted_at": None,
                "remote": any(
                    "remote" in (loc.get("name", "").lower()) for loc in job.get("locations", [])
                ),
                "language": "en",
                "tags": {"board": "greenhouse", "org": self.org},
            }
