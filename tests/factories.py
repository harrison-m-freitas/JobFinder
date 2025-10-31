# tests/factories.py
from __future__ import annotations

import random
from collections.abc import Callable
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from job_finder.db.models.company import Company
from job_finder.db.models.job import Job


def company_factory(db: Session) -> Callable[..., Company]:
    def _make(**overrides) -> Company:
        c = Company(
            name=overrides.get("name", f"Company-{uuid4().hex[:8]}"),
            country=overrides.get("country", "BR"),
            city=overrides.get("city", "São Paulo"),
        )
        db.add(c)
        db.commit()
        db.refresh(c)
        return c

    return _make


def job_factory(db: Session, default_company: Company | None = None) -> Callable[..., Job]:
    def _make(**overrides) -> Job:
        company = overrides.pop("company", None) or default_company or company_factory(db)()
        now = datetime.now(timezone.utc)
        j = Job(
            external_id=overrides.get("external_id", f"ext-{uuid4().hex[:8]}"),
            source=overrides.get(
                "source", random.choice(["remoteok", "weworkremotely", "remoteco"])
            ),
            source_url=overrides.get("source_url", "https://example.com/job"),
            title=overrides.get("title", "Software Engineer"),
            company_id=company.id,
            location=overrides.get("location", company.city),
            remote=overrides.get("remote", True),
            employment_type=overrides.get("employment_type", "full-time"),
            seniority=overrides.get("seniority", random.choice(["junior", "mid", "senior"])),
            currency=overrides.get("currency", "USD"),
            salary_min=overrides.get("salary_min", 60000),
            salary_max=overrides.get("salary_max", 120000),
            language=overrides.get("language", "en"),
            posted_at=overrides.get("posted_at", now),
            scraped_at=overrides.get("scraped_at", now),
        )
        db.add(j)
        db.commit()
        db.refresh(j)
        return j

    return _make
