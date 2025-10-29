FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /work

RUN apt-get update && apt-get install -y --no-install-recommends \
       build-essential curl ca-certificates git tini && \
     rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md /work/
COPY src /work/src
RUN pip install --upgrade pip && pip install -e ".[api,airflow3,scraping]"

COPY . /work

ENTRYPOINT ["/usr/bin/tini", "--"]
