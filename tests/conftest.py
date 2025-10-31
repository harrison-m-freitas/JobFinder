# tests/conftest.py
from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from sqlalchemy.orm import Session

from tests.factories import company_factory as _company_factory
from tests.factories import job_factory as _job_factory

# 1) Configura variável de ambiente para usar banco de dados de teste
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ.setdefault("APP_ENV", "test")

# 2) Importa engine e metadata
# 3) Garante que modelos foram registrados
import job_finder.db.models.company  # noqa: F401
import job_finder.db.models.job  # noqa: F401
from job_finder.db.models.base import Base
from job_finder.db.session import engine

try:
    from job_finder.db.session import SessionLocal
except ImportError:
    from sqlalchemy.orm import sessionmaker

    SessionLocal = sessionmaker(bind=engine)


@pytest.fixture
def db() -> Iterator[Session]:
    session = SessionLocal()
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="session", autouse=True)
def _create_schema():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def company_factory(db: Session):
    return _company_factory(db)


@pytest.fixture
def job_factory(db: Session):
    return _job_factory(db)
