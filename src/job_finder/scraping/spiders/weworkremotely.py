from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Any
from urllib.parse import urljoin

import scrapy
from scrapy.http import Response

BASE = "https://weworkremotely.com"


class WeWorkRemotelySpider(scrapy.Spider):
    name = "weworkremotely"
    allowed_domains = ["weworkremotely.com"]
    start_urls = [f"{BASE}/remote-jobs/search?term=developer"]

    def parse(self, response: Response) -> Iterable[scrapy.Request | dict[str, Any]]:
        for job in response.css("section.jobs article li.feature"):
            link = job.css("a::attr(href)").get()
            title = job.css("span.title::text").get()
            company = job.css("span.company::text").get()
            posted = job.css("time::attr(datetime)").get()
            url = urljoin(BASE, link)
            yield {
                "source": self.name,
                "external_id": link.rsplit("/", 1)[-1] if link else None,
                "source_url": url,
                "title": title,
                "company_name": company,
                "posted_at": datetime.fromisoformat(posted) if posted else None,
                "remote": True,
                "language": "en",
                "tags": {"board": "weworkremotely"},
            }

        next_page = response.css("a.next_page::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
