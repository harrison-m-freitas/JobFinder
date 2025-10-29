# =========================
# Makefile — JobFinder
# =========================

# -------- Config --------
COMPOSE     ?= docker compose
APP         ?= app
ENV_FILE    ?= .env
ENV_SAMPLE  ?= .env.example

# Em CI (sem TTY) usamos -T; localmente deixamos interativo
ifdef CI
TTY := -T
else
TTY :=
endif

# Wrapper do compose com env-file explícito
COMPOSE_CMD := $(COMPOSE) --env-file $(ENV_FILE)
CONTAINER_PORT := 8000

# Alvo padrão
.DEFAULT_GOAL := help

.PHONY: help ensure-env up down logs shell format lint type test migrate-new migrate-up \
        crawl-wwr crawl-remoteok crawl-remoteco crawl-greenhouse crawl-workable \
        api api-up api-stop api-log print-env

# -------- Ajuda --------
help:
	@echo "Comandos disponíveis:"
	@echo "  make up                - sobe os serviços (build + detach)"
	@echo "  make down              - derruba os serviços e volumes"
	@echo "  make logs              - tail dos logs (100 linhas)"
	@echo "  make shell             - bash no contêiner $(APP)"
	@echo "  make format            - black + ruff --fix"
	@echo "  make lint              - ruff"
	@echo "  make type              - mypy src"
	@echo "  make test              - pytest"
	@echo "  make migrate-new name=<slug>  - cria revisão Alembic"
	@echo "  make migrate-up        - aplica migrações até head"
	@echo "  make crawl-wwr         - scrapy crawl weworkremotely"
	@echo "  make crawl-remoteok    - scrapy crawl remoteok"
	@echo "  make crawl-remoteco    - scrapy crawl remoteco"
	@echo "  make crawl-greenhouse org=<org> - scrapy crawl greenhouse"
	@echo "  make crawl-workable   org=<org> - scrapy crawl workable"
	@echo "  make api               - inicia uvicorn dentro do contêiner"
	@echo "  make api-up            - sobe serviços e inicia uvicorn"
	@echo "  make print-env         - imprime caminho do env-file efetivo"

# -------- Util --------
print-env:
	@echo "Usando env-file: $(ENV_FILE)"
	@if [ -f "$(ENV_FILE)" ]; then echo "OK: $(ENV_FILE) encontrado"; else echo "WARN: $(ENV_FILE) não existe"; fi

# Garante que $(ENV_FILE) exista; se não, copia do sample ou cria mínimo (sem heredoc)
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
				echo "# Exemplos comuns (ajuste aos seus serviços):"; \
				echo "# DATABASE_URL=postgresql+psycopg://jobfinder:jobfinder@db:5432/jobfinder"; \
				echo "# REDIS_URL=redis://redis:6379/0"; \
				echo "# AIRFLOW__CORE__EXECUTOR=LocalExecutor"; \
				echo "# AIRFLOW__CORE__LOAD_EXAMPLES=False"; \
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
# Sobe serviços e inicia o Uvicorn em background no contêiner (porta interna FIXA 8000).
# O host usa APP_PORT (no .env) para o mapeamento HOST:APP_PORT -> CONTAINER:8000
api: up
	$(COMPOSE_CMD) exec $(TTY) $(APP) bash -lc "\
		if [ -f /tmp/uvicorn.pid ] && kill -0 \$$(cat /tmp/uvicorn.pid) 2>/dev/null; then \
			echo 'Uvicorn já em execução (PID=' \$$(cat /tmp/uvicorn.pid) ')'; \
		else \
			nohup uvicorn job_finder.api.main:app --host 0.0.0.0 --port $(CONTAINER_PORT) \
				> /tmp/uvicorn.log 2>&1 & echo \$\$! > /tmp/uvicorn.pid; \
			echo 'Uvicorn iniciado (PID=' \$$(cat /tmp/uvicorn.pid) ')'; \
		fi"

api-up: ensure-env
	$(COMPOSE_CMD) up -d
	$(COMPOSE_CMD) exec $(TTY) $(APP) bash -lc "\
		if [ -f /tmp/uvicorn.pid ] && kill -0 \$$(cat /tmp/uvicorn.pid) 2>/dev/null; then \
			echo 'Uvicorn já em execução (PID=' \$$(cat /tmp/uvicorn.pid) ')'; \
		else \
      nohup uvicorn job_finder.api.main:app --host 0.0.0.0 --port $(CONTAINER_PORT) \
				> /tmp/uvicorn.log 2>&1 & echo \$\$! > /tmp/uvicorn.pid; \
			echo 'Uvicorn iniciado (PID=' \$$(cat /tmp/uvicorn.pid) ')'; \
		fi"

# Para o Uvicorn em background dentro do contêiner
api-stop: up
	$(COMPOSE_CMD) exec $(TTY) $(APP) bash -lc "\
		if [ -f /tmp/uvicorn.pid ] && kill -0 \$$(cat /tmp/uvicorn.pid) 2>/dev/null; then \
			kill \$$(cat /tmp/uvicorn.pid) && rm -f /tmp/uvicorn.pid && echo 'Uvicorn parado.'; \
		else \
			echo 'Uvicorn não está em execução.'; \
		fi"

# Mostra o log do Uvicorn em tempo real (dentro do contêiner)
api-log: up
	$(COMPOSE_CMD) exec $(TTY) $(APP) bash -lc "tail -n 200 -f /tmp/uvicorn.log || true"
