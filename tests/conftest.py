# tests/conftest.py
from __future__ import annotations

import os

import pytest

# 1) Força DB de teste ANTES de qualquer import do app
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

# 2) Importa engine e metadata
# 3) Garante que modelos foram registrados
import job_finder.db.models.company  # noqa: F401
import job_finder.db.models.job  # noqa: F401
from job_finder.db.models.base import Base
from job_finder.db.session import engine


@pytest.fixture(scope="session", autouse=True)
def _create_schema():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
