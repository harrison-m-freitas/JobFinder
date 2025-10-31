# src/job_finder/scripts/seed.py
from __future__ import annotations

import argparse
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from job_finder.db.models.company import Company
from job_finder.db.models.job import Job
from job_finder.db.models.skill import Skill
from job_finder.db.session import SessionLocal

COMPANY_SAMPLES = [
    ("Acme Inc", "BR", "São Paulo"),
    ("Globex", "US", "New York"),
    ("Initech", "CA", "Toronto"),
    ("Umbrella", "UK", "London"),
    ("Stark Industries", "US", "Los Angeles"),
    ("Wayne Enterprises", "US", "Gotham"),
    ("Oscorp", "US", "New York"),
    ("Wonka Industries", "UK", "London"),
    ("Hooli", "US", "Palo Alto"),
    ("Vehement Capital Partners", "DE", "Berlin"),
    ("Star Labs", "US", "Metropolis"),
    ("Cyberdyne Systems", "US", "San Francisco"),
    ("Hogwarts School", "UK", "Hogsmeade"),
    ("Gekko & Co", "US", "New York"),
]

SKILL_SAMPLES = [
    ("python", "language"),
    ("typescript", "language"),
    ("sql", "database"),
    ("aws", "cloud"),
    ("docker", "devops"),
    ("kubernetes", "devops"),
    ("react", "framework"),
    ("django", "framework"),
    ("flask", "framework"),
    ("nodejs", "runtime"),
    ("networking", "concept"),
    ("data structures", "concept"),
    ("algorithms", "concept"),
    ("ci/cd", "devops"),
    ("microservices", "architecture"),
    ("graphql", "api"),
    ("rest", "api"),
    ("linux", "os"),
    ("git", "tool"),
    ("testing", "concept"),
    ("sql", "language"),
    ("snowflake", "database"),
    ("terraform", "devops"),
    ("kafka", "tool"),
    ("kubernetes", "orchestration"),
    ("docker", "containerization"),
    ("prometheus", "monitoring"),
    ("grafana", "monitoring"),
    ("elasticsearch", "search"),
    ("logstash", "logging"),
    ("kibana", "logging"),
    ("rabbitmq", "messaging"),
    ("redis", "caching"),
    ("memcached", "caching"),
]


def _ensure_skills(db: Session) -> None:
    existing = {s.name for s in db.execute(select(Skill)).scalars().all()}
    to_add = [Skill(name=n, category=c) for n, c in SKILL_SAMPLES if n not in existing]
    if to_add:
        db.add_all(to_add)
        db.commit()


def _pick(seq: list[Any]) -> Any:
    return secrets.choice(seq)


def _rand_bool() -> bool:
    return bool(secrets.randbits(1))


def _rand_int(a: int, b: int) -> int:
    return secrets.randbelow(b - a + 1) + a


def seed_minimal(db: Session) -> None:
    """Cria um conjunto pequeno e determinístico."""
    _ensure_skills(db)

    companies = []
    for name, country, city in COMPANY_SAMPLES[:3]:
        c = db.scalar(select(Company).where(Company.name == name))
        if not c:
            c = Company(name=name, country=country, city=city)
            db.add(c)
            db.commit()
            db.refresh(c)
        companies.append(c)

    now = datetime.now(timezone.utc)
    jobs = []
    for i, c in enumerate(companies, start=1):
        j = Job(
            external_id=f"seed-min-{i}",
            source="seed",
            source_url=f"https://example.com/jobs/seed-min-{i}",
            title=f"Software Engineer {i}",
            company_id=c.id,
            location=c.city,
            remote=_rand_bool(),
            employment_type="full-time",
            seniority=_pick(["junior", "mid", "senior"]),
            currency="USD",
            salary_min=60000,
            salary_max=120000,
            language="en",
            posted_at=now - timedelta(days=i),
            scraped_at=now,
        )
        jobs.append(j)

    db.add_all(jobs)
    db.commit()
    print(f"[seed] minimal: {len(jobs)} jobs, {len(companies)} companies")


def seed_demo(db: Session, jobs_total: int = 50, companies_total: int = 10) -> None:
    """Dataset maior para brincar na API."""
    _ensure_skills(db)

    # Companies
    created_companies = []
    for i in range(companies_total):
        name = f"DemoCo {i:02d}"
        c = db.scalar(select(Company).where(Company.name == name))
        if not c:
            c = Company(
                name=name,
                country=_pick(["BR", "US", "CA", "UK", "DE"]),
                city=_pick(["São Paulo", "Rio", "NYC", "Toronto", "Berlin"]),
            )
            db.add(c)
            db.commit()
            db.refresh(c)
        created_companies.append(c)

    # Jobs
    now = datetime.now(timezone.utc)
    jobs = []
    for i in range(jobs_total):
        c = _pick(created_companies)
        sal_min = _pick([50000, 70000, 90000, 110000])
        sal_max = sal_min + _pick([15000, 30000, 50000])
        j = Job(
            external_id=f"seed-demo-{i}",
            source=_pick(["weworkremotely", "remoteok", "remoteco", "workable"]),
            source_url=f"https://example.com/jobs/seed-demo-{i}",
            title=_pick(["Backend Engineer", "Data Engineer", "Full-Stack Dev", "SRE"]),
            company_id=c.id,
            location=c.city,
            remote=_rand_bool(),
            employment_type=_pick(["full-time", "contract"]),
            seniority=_pick(["junior", "mid", "senior"]),
            currency="USD",
            salary_min=sal_min,
            salary_max=sal_max,
            language=_pick(["en", "pt"]),
            posted_at=now - timedelta(days=_rand_int(0, 30)),
            scraped_at=now,
        )
        jobs.append(j)

    db.add_all(jobs)
    db.commit()
    print(f"[seed] demo: {len(jobs)} jobs, {len(created_companies)} companies")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed de dados de desenvolvimento")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("minimal", help="Seed mínimo determinístico")
    sub.add_parser("clear", help="Apaga todos os dados (DANGER)")

    p_demo = sub.add_parser("demo", help="Seed demo maior")
    p_demo.add_argument("--jobs", type=int, default=50)
    p_demo.add_argument("--companies", type=int, default=10)

    args = parser.parse_args()
    db: Session = SessionLocal()
    try:
        if args.cmd == "clear":
            # drop all conteúdo (ordem importa por FKs)
            db.query(Job).delete()
            db.query(Company).delete()
            db.query(Skill).delete()
            db.commit()
            print("[seed] clear ok")
            return

        # garante schema ok (assume que Alembic foi rodado)
        if args.cmd == "minimal":
            seed_minimal(db)
        elif args.cmd == "demo":
            seed_demo(db, jobs_total=args.jobs, companies_total=args.companies)
    finally:
        db.close()


if __name__ == "__main__":
    main()
