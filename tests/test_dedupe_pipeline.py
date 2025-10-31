from __future__ import annotations

from datetime import datetime, timezone

import pytest
from scrapy.exceptions import DropItem

from job_finder.db.models.job import Job
from job_finder.scraping.pipelines.dedupe_pipeline import DedupePipeline


class _DummySpider:
    name = "dummy"


def _existing_job(db) -> Job:
    now = datetime.now(timezone.utc)
    j = Job(
        external_id="ext-123",
        source="remoteok",
        source_url="https://example.com/ok",
        title="Backend Engineer",
        description_text="Build APIs",
        location="Remote",
        remote=True,
        employment_type="full-time",
        seniority="mid",
        currency="USD",
        salary_min=60000,
        salary_max=120000,
        language="en",
        posted_at=now,
        scraped_at=now,
    )
    db.add(j)
    db.commit()
    db.refresh(j)
    return j


def test_dedupe_drops_when_unchanged(db):
    # Arrange: registra um job existente
    j = _existing_job(db)
    pipeline = DedupePipeline()
    spider = _DummySpider()
    pipeline.open_spider(spider)
    try:
        item = {
            "source": j.source,
            "external_id": j.external_id,
            "source_url": j.source_url,
            "title": j.title,
            "company_name": None,
            "location": j.location,
            "remote": j.remote,
            "employment_type": j.employment_type,
            "seniority": j.seniority,
            "currency": j.currency,
            "salary_min": float(j.salary_min),
            "salary_max": float(j.salary_max),
            "tags": None,
            "language": j.language,
            "posted_at": j.posted_at,
            "description_html": None,
            "description_text": j.description_text,
        }
        with pytest.raises(DropItem):
            pipeline.process_item(item, spider)
    finally:
        pipeline.close_spider(spider)


def test_dedupe_passes_when_changed(db):
    # Arrange
    j = _existing_job(db)
    pipeline = DedupePipeline()
    spider = _DummySpider()
    pipeline.open_spider(spider)
    try:
        # título alterado -> deve passar (sem DropItem)
        item = {
            "source": j.source,
            "external_id": j.external_id,
            "source_url": j.source_url,
            "title": j.title + " II",
            "company_name": None,
            "location": j.location,
            "remote": j.remote,
            "employment_type": j.employment_type,
            "seniority": j.seniority,
            "currency": j.currency,
            "salary_min": float(j.salary_min),
            "salary_max": float(j.salary_max),
            "tags": None,
            "language": j.language,
            "posted_at": j.posted_at,
            "description_html": None,
            "description_text": j.description_text,
        }
        out = pipeline.process_item(item, spider)
        assert out is item
    finally:
        pipeline.close_spider(spider)
