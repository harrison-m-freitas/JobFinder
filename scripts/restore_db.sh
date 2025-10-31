#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "uso: $0 backups/<arquivo>.dump"
  exit 1
fi

DUMP_LOCAL_PATH="$1"
if [ ! -f "$DUMP_LOCAL_PATH" ]; then
  echo "arquivo não encontrado: $DUMP_LOCAL_PATH"
  exit 1
fi

DB_HOST="${POSTGRES_HOST:-db}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-jobhunter}"
DB_USER="${POSTGRES_USER:-app}"
DB_PASS="${POSTGRES_PASSWORD:-app}"

BASENAME="$(basename "$DUMP_LOCAL_PATH")"

echo "[restore] copiando dump para o container..."
docker compose cp "$DUMP_LOCAL_PATH" db:/backups/"$BASENAME"

echo "[restore] restaurando ${BASENAME} em ${DB_NAME} ..."
docker compose exec -T db sh -lc "export PGPASSWORD='${DB_PASS}'; pg_restore -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d ${DB_NAME} -c -j 2 /backups/${BASENAME}"

echo "[restore] ok"
