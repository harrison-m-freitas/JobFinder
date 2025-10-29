from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from job_finder.db.models.base import Base  # noqa: F401
from job_finder.db.models.company import Company  # noqa: F401
from job_finder.db.models.job import Job  # noqa: F401
from job_finder.db.models.job_benefit import JobBenefit  # noqa: F401
from job_finder.db.models.job_skill import JobSkill  # noqa: F401
from job_finder.db.models.scraping_log import ScrapingLog  # noqa: F401
from job_finder.db.models.skill import Skill  # noqa: F401

config = context.config

# Allow DATABASE_URL from env to override ini
db_url = os.getenv("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
