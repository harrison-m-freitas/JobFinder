# src/job_finder/scraping/spiders/remoteco.py
from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Any

import scrapy
from scrapy.http import Response


class RemoteCoSpider(scrapy.Spider):
    name = "remoteco"
    allowed_domains = ["remote.co"]
    start_urls = ["https://remote.co/remote-jobs/developer/"]

    def parse(self, response: Response) -> Iterable[scrapy.Request | dict[str, Any]]:
        for card in response.css("div.card"):
            link = card.css("a.card-title::attr(href)").get()
            title = card.css("a.card-title::text").get()
            company = card.css("div.company::text").get()
            date = card.css("time::attr(datetime)").get()
            yield {
                "source": self.name,
                "external_id": link.strip("/").split("/")[-1] if link else None,
                "source_url": response.urljoin(link) if link else response.url,
                "title": (title or "").strip(),
                "company_name": (company or "").strip() or None,
                "posted_at": datetime.fromisoformat(date) if date else None,
                "remote": True,
                "language": "en",
                "tags": {"board": "remote.co"},
            }

        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
