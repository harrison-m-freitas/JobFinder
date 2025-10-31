from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Any
from urllib.parse import urljoin

import scrapy
from scrapy.http import Response

BASE = "https://remoteok.com"


class RemoteOKSpider(scrapy.Spider):
    name = "remoteok"
    allowed_domains = ["remoteok.com"]
    start_urls = [f"{BASE}/remote-dev-jobs"]
    custom_settings = {
        "CONCURRENT_REQUESTS": 2,
        "DOWNLOAD_DELAY": 1.5,
    }

    def parse(self, response: Response) -> Iterable[dict[str, Any]]:
        for row in response.css("tr.job"):
            link = row.css("a.preventLink::attr(href)").get()
            title = row.css("td.position h2::text").get()
            company = row.css("td.company h3::text").get()
            date = row.css("time::attr(datetime)").get()
            url = urljoin(BASE, link) if link else response.url
            yield {
                "source": self.name,
                "external_id": link.strip("/").split("/")[-1] if link else None,
                "source_url": url,
                "title": title,
                "company_name": company,
                "posted_at": datetime.fromisoformat(date) if date else None,
                "remote": True,
                "language": "en",
                "tags": {"board": "remoteok"},
            }
