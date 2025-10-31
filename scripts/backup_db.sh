#!/usr/bin/env bash

DB_HOST="${POSTGRES_HOST:-db}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-jobhunter}"
DB_USER="${POSTGRES_USER:-app}"
DB_PASS="${POSTGRES_PASSWORD:-app}"

STAMP="$(date -u +'%Y%m%dT%H%M%SZ')"
FILE="/backups/${DB_NAME}_${STAMP}.dump"

echo "[backup] criando ${FILE} ..."
docker compose exec -T db sh -lc "export PGPASSWORD='${DB_PASS}'; pg_dump -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d ${DB_NAME} -Fc -Z9 -j 2 -f '${FILE}'"

echo "[backup] ok -> $(pwd)/backups/$(basename "$FILE")"
