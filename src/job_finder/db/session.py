from __future__ import annotations

from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from job_finder.settings import settings

url = settings.sqlalchemy_url
engine_kwargs: dict[str, Any] = dict(pool_pre_ping=True, future=True)
if url.startswith("sqlite"):
    engine_kwargs.update(connect_args={"check_same_thread": False})
    if url.endswith(":memory:"):
        engine_kwargs.update(poolclass=StaticPool)
engine = create_engine(url, **engine_kwargs)
SessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True
)
