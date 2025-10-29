# src/job_finder/scraping/schemas.py
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, HttpUrl, field_validator


class JobIngest(BaseModel):
    source: str
    external_id: str | None = None
    source_url: HttpUrl
    title: str
    company_name: str | None = None
    location: str | None = None
    remote: bool = False
    employment_type: str | None = None
    seniority: str | None = None
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    salary_min: float | None = None
    salary_max: float | None = None
    tags: dict[str, Any] | None = None
    language: str | None = Field(default=None, min_length=2, max_length=5)
    posted_at: datetime | None = None
    description_html: str | None = None
    description_text: str | None = None

    @field_validator("salary_max")
    @classmethod
    def _salary_order(cls, value: float | None, info: Any) -> float | None:
        min_value = getattr(info, "data", {}).get("salary_min") if info is not None else None
        if value is not None and isinstance(min_value, int | float) and value < float(min_value):
            raise ValueError("salary_max < salary_min")
        return value
