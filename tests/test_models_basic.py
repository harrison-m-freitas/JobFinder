from __future__ import annotations

from datetime import datetime, timezone

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from job_finder.db.models.company import Company
from job_finder.db.models.job import Job
from job_finder.db.session import SessionLocal


@pytest.fixture
def db() -> Session:
    return SessionLocal()


def test_insert_company_and_job(db: Session) -> None:
    c = Company(name="Acme Inc", country="BR", city="São Paulo")
    db.add(c)
    db.commit()
    db.refresh(c)

    j1 = Job(
        external_id="123",
        source="weworkremotely",
        source_url="https://example.com/jobs/123",
        title="Backend Engineer",
        company_id=c.id,
        scraped_at=datetime.now(timezone.utc),
        remote=True,
        language="pt",
    )
    db.add(j1)
    db.commit()

    rows = db.execute(text("select count(*) from jobs")).scalar_one()
    assert rows == 1


def test_unique_source_external(db: Session) -> None:
    j1 = Job(
        external_id="dup-1",
        source="remoteok",
        source_url="https://example.com/jobs/dup-1",
        title="Data Engineer",
        scraped_at=datetime.now(timezone.utc),
    )
    j2 = Job(
        external_id="dup-1",
        source="remoteok",
        source_url="https://example.com/jobs/dup-1",
        title="Data Engineer 2",
        scraped_at=datetime.now(timezone.utc),
    )
    db.add_all([j1, j2])
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_list_two_jobs(db, job_factory):
    j1 = job_factory(title="Backend Engineer")
    j2 = job_factory(title="Data Engineer")
    assert j1.id != j2.id
