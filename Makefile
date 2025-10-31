# =========================
# Makefile — JobFinder
# =========================

# -------- Config --------
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

COMPOSE     ?= docker compose
APP         ?= app
DB          ?= db
ENV_FILE    ?= .env
ENV_SAMPLE  ?= .env.example

# Em CI (sem TTY) usamos -T; localmente deixamos interativo
ifdef CI
TTY := -T
else
TTY :=
endif

# Wrapper do compose com env-file explícito (para up/exec/etc.)
COMPOSE_CMD := $(COMPOSE) --env-file $(ENV_FILE)

CONTAINER_PORT := 8000
BACKUP_DIR     ?= backups
# Parâmetros default para seed demo (podem ser sobrescritos: make seed-demo JOBS=100 COMPANIES=15)
JOBS       ?= 50
COMPANIES  ?= 10

# Alvo padrão
.DEFAULT_GOAL := help

.PHONY: help ensure-env up down logs shell format lint type test migrate-new migrate-up \
        backup restore backup-list backup-prune \
        seed-min seed-demo \
        crawl-wwr crawl-remoteok crawl-remoteco crawl-greenhouse crawl-workable \
        api api-up api-stop api-log print-env psql db-shell

# -------- Ajuda --------
help:
	@echo "Comandos disponíveis:"
	@echo "  make up                      - sobe os serviços (build + detach)"
	@echo "  make down                    - derruba os serviços e volumes"
	@echo "  make logs                    - tail dos logs (100 linhas)"
	@echo "  make shell                   - bash no contêiner $(APP)"
	@echo "  make format                  - black + ruff --fix"
	@echo "  make lint                    - ruff"
	@echo "  make type                    - mypy src"
	@echo "  make test                    - pytest"
	@echo "  make migrate-new name=<slug> - cria revisão Alembic"
	@echo "  make migrate-up              - aplica migrações até head"
	@echo "  make backup                  - cria backup do banco (.dump custom)"
	@echo "  make restore FILE=backups/<dump>.dump - restaura um backup"
	@echo "  make backup-list             - lista dumps em $(BACKUP_DIR)"
	@echo "  make backup-prune DAYS=7     - apaga dumps mais antigos que N dias (default 7)"
	@echo "  make seed-min                - popula DB com dados mínimos"
	@echo "  make seed-demo JOBS=50 COMPANIES=10 - popula DB com dados de demo"
	@echo "  make crawl-wwr               - scrapy crawl weworkremotely"
	@echo "  make crawl-remoteok          - scrapy crawl remoteok"
	@echo "  make crawl-remoteco          - scrapy crawl remoteco"
	@echo "  make crawl-greenhouse org=<org> - scrapy crawl greenhouse"
	@echo "  make crawl-workable org=<org>   - scrapy crawl workable"
	@echo "  make api                     - inicia uvicorn dentro do contêiner"
	@echo "  make api-up                  - sobe serviços e inicia uvicorn"
	@echo "  make api-stop                - para o uvicorn em background"
	@echo "  make api-log                 - tail do log do uvicorn"
	@echo "  make psql                    - abre psql no container do Postgres"
	@echo "  make print-env               - imprime caminho do env-file efetivo"

# -------- Util --------
print-env:
	@echo "Usando env-file: $(ENV_FILE)"
	@if [ -f "$(ENV_FILE)" ]; then echo "OK: $(ENV_FILE) encontrado"; else echo "WARN: $(ENV_FILE) não existe"; fi

# Garante que $(ENV_FILE) exista; se não, copia do sample ou cria mínimo
ensure-env:
	@if [ ! -f "$(ENV_FILE)" ]; then \
		if [ -f "$(ENV_SAMPLE)" ]; then \
			echo ">> Criando $(ENV_FILE) a partir de $(ENV_SAMPLE)"; \
			cp "$(ENV_SAMPLE)" "$(ENV_FILE)"; \
		else \
			echo ">> Criando $(ENV_FILE) mínimo (edite depois)"; \
			{ \
				echo "# Ambiente mínimo — ajuste conforme seu docker-compose"; \
				echo "APP_ENV=dev"; \
				echo "LOG_LEVEL=INFO"; \
				echo "# DATABASE_URL=postgresql+psycopg://app:app@db:5432/jobhunter"; \
			} > "$(ENV_FILE)"; \
		fi; \
	fi

# -------- Docker --------
up: ensure-env
	$(COMPOSE_CMD) up -d --build

down:
	$(COMPOSE_CMD) down -v

logs: up
	$(COMPOSE_CMD) logs -f --tail=100

shell: up
	$(COMPOSE_CMD) exec $(APP) bash

db-shell: up
	$(COMPOSE_CMD) exec $(DB) sh

psql: up
	$(COMPOSE_CMD) exec $(DB) sh -lc 'export PGPASSWORD="$${POSTGRES_PASSWORD:-app}"; psql -h "$${POSTGRES_HOST:-localhost}" -U "$${POSTGRES_USER:-app}" -d "$${POSTGRES_DB:-jobhunter}"'

# -------- Qualidade --------
format: up
	$(COMPOSE_CMD) exec $(TTY) $(APP) bash -lc "black . && ruff --fix ."

lint: up
	$(COMPOSE_CMD) exec $(TTY) $(APP) bash -lc "ruff ."

type: up
	$(COMPOSE_CMD) exec $(TTY) $(APP) bash -lc "mypy src"

test: up
	$(COMPOSE_CMD) exec $(TTY) $(APP) bash -lc "pytest"

# -------- Migrações --------
migrate-new: up
	@if [ -z "$(name)" ]; then \
		echo "ERRO: informe o nome da revisão: make migrate-new name=<slug>"; \
		exit 2; \
	fi
	$(COMPOSE_CMD) exec $(TTY) $(APP) bash -lc "alembic -c alembic.ini revision -m '$(name)'"

migrate-up: up
	$(COMPOSE_CMD) exec $(TTY) $(APP) bash -lc "alembic -c alembic.ini upgrade head"

# -------- Backup / Restore --------
# Gera dump custom (-Fc) dentro do container e copia para $(BACKUP_DIR)
backup: up
	@mkdir -p "$(BACKUP_DIR)"
	@STAMP=$$(date -u +'%Y%m%dT%H%M%SZ'); \
	DEST="$(BACKUP_DIR)/$${POSTGRES_DB:-jobhunter}_$${STAMP}.dump"; \
	echo ">> Gerando dump dentro do container..."; \
	$(COMPOSE_CMD) exec -T $(DB) sh -lc 'export PGPASSWORD="$${POSTGRES_PASSWORD:-app}"; \
	 pg_dump -h "$${POSTGRES_HOST:-localhost}" -p "$${POSTGRES_PORT:-5432}" \
	  -U "$${POSTGRES_USER:-app}" -d "$${POSTGRES_DB:-jobhunter}" \
	  -Fc -Z9 -j 2 -f /tmp/backup.dump'; \
	echo ">> Copiando dump para o host: $$DEST"; \
	$(COMPOSE) cp $(DB):/tmp/backup.dump "$$DEST"; \
	$(COMPOSE_CMD) exec -T $(DB) sh -lc 'rm -f /tmp/backup.dump'; \
	echo "OK: $$DEST"

# Restaura a partir de FILE=<caminho do dump>
restore: up
	@if [ -z "$(FILE)" ]; then \
		echo "ERRO: informe o dump: make restore FILE=$(BACKUP_DIR)/<arquivo>.dump"; \
		exit 2; \
	fi
	@test -f "$(FILE)" || (echo "ERRO: arquivo não encontrado: $(FILE)"; exit 2)
	@echo ">> Copiando dump para o container..."
	$(COMPOSE) cp "$(FILE)" $(DB):/tmp/restore.dump
	@echo ">> Restaurando dentro do container..."
	$(COMPOSE_CMD) exec -T $(DB) sh -lc 'export PGPASSWORD="$${POSTGRES_PASSWORD:-app}"; \
	 pg_restore -h "$${POSTGRES_HOST:-localhost}" -p "$${POSTGRES_PORT:-5432}" \
	  -U "$${POSTGRES_USER:-app}" -d "$${POSTGRES_DB:-jobhunter}" \
	  -c -j 2 /tmp/restore.dump'
	$(COMPOSE_CMD) exec -T $(DB) sh -lc 'rm -f /tmp/restore.dump'
	@echo "OK: restore concluído de $(FILE)"

backup-list:
	@ls -lh $(BACKUP_DIR)/*.dump 2>/dev/null || echo "(nenhum dump em $(BACKUP_DIR))"

backup-prune:
	@DAYS=$${DAYS:-7}; \
	echo ">> Apagando dumps mais antigos que $$DAYS dias em $(BACKUP_DIR)"; \
	find "$(BACKUP_DIR)" -name '*.dump' -type f -mtime +$$DAYS -print -delete || true

# -------- Seeds --------
seed-min: up
	$(COMPOSE_CMD) exec $(TTY) $(APP) bash -lc "python -m job_finder.scripts.seed minimal"

seed-demo: up
	$(COMPOSE_CMD) exec $(TTY) $(APP) bash -lc "python -m job_finder.scripts.seed demo --jobs $(JOBS) --companies $(COMPANIES)"

# -------- Crawlers --------
crawl-wwr: up
	$(COMPOSE_CMD) exec $(TTY) $(APP) bash -lc "scrapy crawl weworkremotely"

crawl-remoteok: up
	$(COMPOSE_CMD) exec $(TTY) $(APP) bash -lc "scrapy crawl remoteok"

crawl-remoteco: up
	$(COMPOSE_CMD) exec $(TTY) $(APP) bash -lc "scrapy crawl remoteco"

crawl-greenhouse: up
	@if [ -z "$(org)" ]; then \
		echo "ERRO: informe a organização: make crawl-greenhouse org=<org>"; \
		exit 2; \
	fi
	$(COMPOSE_CMD) exec $(TTY) $(APP) bash -lc "scrapy crawl greenhouse -a org=$(org)"

crawl-workable: up
	@if [ -z "$(org)" ]; then \
		echo "ERRO: informe a organização: make crawl-workable org=<org>"; \
		exit 2; \
	fi
	$(COMPOSE_CMD) exec $(TTY) $(APP) bash -lc "scrapy crawl workable -a org=$(org)"

# -------- API --------
api: up
	$(COMPOSE_CMD) exec $(TTY) $(APP) bash -lc '\
		if [ -f /tmp/uvicorn.pid ] && kill -0 "$$(cat /tmp/uvicorn.pid)" 2>/dev/null; then \
			echo "Uvicorn já em execução (PID=$$(cat /tmp/uvicorn.pid))"; \
		else \
			nohup uvicorn job_finder.api.main:app --host 0.0.0.0 --port $(CONTAINER_PORT) \
				> /tmp/uvicorn.log 2>&1 & echo $$! > /tmp/uvicorn.pid; \
			echo "Uvicorn iniciado (PID=$$(cat /tmp/uvicorn.pid))"; \
		fi'

api-up: ensure-env
	$(COMPOSE_CMD) up -d
	$(COMPOSE_CMD) exec $(TTY) $(APP) bash -lc '\
		if [ -f /tmp/uvicorn.pid ] && kill -0 "$$(cat /tmp/uvicorn.pid)" 2>/dev/null; then \
			echo "Uvicorn já em execução (PID=$$(cat /tmp/uvicorn.pid))"; \
		else \
			nohup uvicorn job_finder.api.main:app --host 0.0.0.0 --port $(CONTAINER_PORT) \
				> /tmp/uvicorn.log 2>&1 & echo $$! > /tmp/uvicorn.pid; \
			echo "Uvicorn iniciado (PID=$$(cat /tmp/uvicorn.pid))"; \
		fi'

api-stop: up
	$(COMPOSE_CMD) exec $(TTY) $(APP) bash -lc '\
		if [ -f /tmp/uvicorn.pid ] && kill -0 "$$(cat /tmp/uvicorn.pid)" 2>/dev/null; then \
			kill "$$(cat /tmp/uvicorn.pid)" && rm -f /tmp/uvicorn.pid && echo "Uvicorn parado."; \
		else \
			echo "Uvicorn não está em execução."; \
		fi'

api-log: up
	$(COMPOSE_CMD) exec $(TTY) $(APP) bash -lc 'tail -n 200 -f /tmp/uvicorn.log || true'
