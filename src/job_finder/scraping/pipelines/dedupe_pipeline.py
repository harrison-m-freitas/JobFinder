# src/job_finder/scraping/pipelines/dedupe_pipeline.py
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any

import scrapy
import structlog
from scrapy.exceptions import DropItem
from sqlalchemy import select
from sqlalchemy.orm import Session

from job_finder.db.models.job import Job
from job_finder.db.session import SessionLocal
from job_finder.scraping.schemas import JobIngest

log = structlog.get_logger(__name__)


def _normalize_for_hash(d: dict[str, Any]) -> dict[str, Any]:
    """Normaliza estrutura para um hash estável (strings, floats, isoformat)."""
    out: dict[str, Any] = {}
    for k, v in d.items():
        if isinstance(v, datetime):
            out[k] = v.isoformat()
        elif isinstance(v, (int, float)) or v is None or isinstance(v, bool):
            out[k] = v
        else:
            out[k] = str(v) if v is not None else None
    return out


def _checksum(d: dict[str, Any]) -> str:
    payload = json.dumps(_normalize_for_hash(d), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class DedupePipeline:
    def open_spider(self, spider: scrapy.Spider) -> None:
        self.db: Session = SessionLocal()

    def close_spider(self, spider: scrapy.Spider) -> None:
        self.db.close()

    def process_item(self, item: dict[str, Any], spider: scrapy.Spider) -> dict[str, Any]:
        data = JobIngest(**item)
        # Sem external_id não dá para deduplicar fortemente — deixa seguir
        if not data.external_id:
            return item
        # Busca o job existente
        exists = self.db.scalar(
            select(Job).where(Job.source == data.source, Job.external_id == data.external_id)
        )
        if not exists:
            return item
        current = {
            "title": exists.title,
            "description_html": exists.description_html,
            "description_text": exists.description_text,
            "location": exists.location,
            "remote": exists.remote,
            "employment_type": exists.employment_type,
            "seniority": exists.seniority,
            "currency": exists.currency,
            "salary_min": float(exists.salary_min) if exists.salary_min is not None else None,
            "salary_max": float(exists.salary_max) if exists.salary_max is not None else None,
            "language": exists.language,
            "posted_at": exists.posted_at,
        }
        incoming = {
            "title": data.title,
            "description_html": data.description_html,
            "description_text": data.description_text,
            "location": data.location,
            "remote": data.remote,
            "employment_type": data.employment_type,
            "seniority": data.seniority,
            "currency": data.currency,
            "salary_min": data.salary_min,
            "salary_max": data.salary_max,
            "language": data.language,
            "posted_at": data.posted_at,
        }
        if _checksum(current) == _checksum(incoming):
            log.info(
                "drop_duplicate_unchanged",
                source=data.source,
                external_id=data.external_id,
            )
            raise DropItem("duplicate_unchanged")
        return item
