from __future__ import annotations

import os
from datetime import datetime

from fastapi import FastAPI, Query
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Histogram,
    generate_latest,
    multiprocess,
)
from pydantic import BaseModel
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session
from starlette.responses import Response

from job_finder.db.models.company import Company
from job_finder.db.models.job import Job
from job_finder.db.session import SessionLocal

app = FastAPI(title="JobHunter API", version="0.1.0")

REQS = Counter("api_requests_total", "Total API requests", ["path"])
LAT = Histogram("api_latency_ms", "API latency (ms)", buckets=(10, 25, 50, 100, 250, 500, 1000))


class JobOut(BaseModel):
    id: str
    title: str
    company: str | None = None
    location: str | None = None
    remote: bool
    salary_min: float | None = None
    salary_max: float | None = None
    posted_at: datetime | None = None
    source: str
    source_url: str


@app.get("/health")
def health() -> dict[str, str]:
    REQS.labels("/health").inc()
    return {"status": "ok"}


@app.get("/metrics")
def metrics() -> Response:
    if os.getenv("PROMETHEUS_MULTIPROC_DIR"):
        registry = CollectorRegistry()
        mp_collect = getattr(multiprocess, "MultiProcessCollector", None)
        if mp_collect is not None:
            mp_collect(registry)
    else:
        payload = generate_latest()
    return Response(payload, media_type=CONTENT_TYPE_LATEST)


@app.get("/jobs", response_model=list[JobOut])
def list_jobs(
    q: str | None = None,
    company: str | None = None,
    location: str | None = None,
    remote: bool | None = None,
    seniority: str | None = None,
    min_salary: float | None = None,
    max_salary: float | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[JobOut]:
    REQS.labels("/jobs").inc()
    with LAT.time():
        db: Session = SessionLocal()
        try:
            J = Job
            conditions = []
            if q:
                conditions.append(or_(J.title.ilike(f"%{q}%"), J.description_text.ilike(f"%{q}%")))
            if company:
                sub = select(Company.id).where(Company.name.ilike(f"%{company}%"))
                conditions.append(J.company_id.in_(sub))
            if location:
                conditions.append(J.location.ilike(f"%{location}%"))
            if remote is not None:
                conditions.append(J.remote.is_(remote))
            if seniority:
                conditions.append(J.seniority.ilike(f"%{seniority}%"))
            if min_salary is not None:
                conditions.append(J.salary_min >= min_salary)
            if max_salary is not None:
                conditions.append(J.salary_max <= max_salary)

            stmt = select(J).where(and_(*conditions)) if conditions else select(J)
            stmt = (
                stmt.order_by(J.posted_at.desc().nullslast(), J.scraped_at.desc())
                .limit(limit)
                .offset(offset)
            )
            rows = db.execute(stmt).scalars().all()
            out = []
            for r in rows:
                out.append(
                    JobOut(
                        id=str(r.id),
                        title=r.title,
                        company=getattr(r.company, "name", None),
                        location=r.location,
                        remote=r.remote,
                        salary_min=float(r.salary_min) if r.salary_min is not None else None,
                        salary_max=float(r.salary_max) if r.salary_max is not None else None,
                        posted_at=r.posted_at,
                        source=r.source,
                        source_url=r.source_url,
                    )
                )
            return out
        finally:
            db.close()
