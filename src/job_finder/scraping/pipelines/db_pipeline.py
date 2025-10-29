# src/job_finder/scraping/pipelines/db_pipeline.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import scrapy
import structlog
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from job_finder.db.models.company import Company
from job_finder.db.models.job import Job
from job_finder.db.session import SessionLocal
from job_finder.scraping.schemas import JobIngest

log = structlog.get_logger(__name__)


class DbPipeline:
    def open_spider(self, spider: scrapy.Spider) -> None:
        self.db: Session = SessionLocal()

    def close_spider(self, spider: scrapy.Spider) -> None:
        self.db.close()

    def _get_or_create_company(self, name: str | None) -> Company | None:
        if not name:
            return None
        company = self.db.scalar(select(Company).where(Company.name == name))
        if company:
            return company
        company = Company(name=name)
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company

    def process_item(self, item: dict[str, Any], spider: scrapy.Spider) -> dict[str, Any]:
        data = JobIngest(**item)
        company = self._get_or_create_company(data.company_name)

        payload: dict[str, Any] = {
            "external_id": data.external_id,
            "source": data.source,
            "source_url": str(data.source_url),
            "title": data.title,
            "description_html": data.description_html,
            "description_text": data.description_text,
            "company_id": getattr(company, "id", None),
            "location": data.location,
            "remote": data.remote,
            "employment_type": data.employment_type,
            "seniority": data.seniority,
            "currency": data.currency,
            "salary_min": data.salary_min,
            "salary_max": data.salary_max,
            "tags": data.tags,
            "language": data.language,
            "posted_at": data.posted_at,
            "scraped_at": datetime.now(timezone.utc),
        }

        stmt = (
            insert(Job)
            .values(**payload)
            .on_conflict_do_update(
                index_elements=["source", "external_id"],
                set_={k: v for k, v in payload.items() if k not in {"source", "external_id"}},
            )
        )
        self.db.execute(stmt)
        self.db.commit()
        log.info("upsert_job", source=data.source, external_id=data.external_id)
        return item
