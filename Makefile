.PHONY: help up down db-logs install install-backend install-frontend seed migrate db-setup backend frontend dev test test-backend test-frontend lint lint-fix clean reset-db env docker-migrate docker-api

help:
	@echo "BiteScore — common commands"
	@echo ""
	@echo "  make up              Start PostgreSQL (Docker)"
	@echo "  make down            Stop PostgreSQL"
	@echo "  make db-logs         Tail Postgres logs"
	@echo "  make install         Install backend + frontend deps"
	@echo "  make install-backend Install Python deps (Poetry)"
	@echo "  make install-frontend Install Node deps (npm)"
	@echo "  make migrate         Run Alembic migrations"
	@echo "  make db-setup        Run migrations + seed demo data"
	@echo "  make seed            Seed demo data (runs migrations first)"
	@echo "  make backend         Migrate DB, then start FastAPI on :8000"
	@echo "  make frontend        Start Nuxt on :3000"
	@echo "  make dev             Print instructions to run backend + frontend"
	@echo "  make docker-migrate  Run migrations via Docker (production image)"
	@echo "  make docker-api      Start Postgres + migrate + API via Docker Compose"
	@echo "  make test            Run backend + frontend tests"
	@echo "  make test-backend    Run backend pytest suite"
	@echo "  make test-frontend   Run frontend vitest suite"
	@echo "  make lint            Run backend ruff lint + format check"
	@echo "  make lint-fix        Auto-fix backend lint and formatting"
	@echo "  make clean           Remove caches and build artifacts"
	@echo "  make reset-db        Wipe DB volume and re-seed"

up:
	docker compose up -d

down:
	docker compose down

db-logs:
	docker compose logs -f postgres

reset-db: down
	docker compose down -v
	docker compose up -d
	@echo "Waiting for Postgres..."
	@sleep 3
	$(MAKE) db-setup

install: install-backend install-frontend

install-backend:
	cd backend && poetry install --with dev

install-frontend:
	cd frontend && npm install

env:
	@test -f backend/.env || cp .env.example backend/.env
	@echo "backend/.env ready"

db-setup: migrate seed

seed: env migrate
	cd backend && poetry run seed

migrate: env
	cd backend && poetry run alembic upgrade head

docker-migrate:
	docker compose -f docker-compose.prod.yml run --rm migrate

docker-api:
	docker compose -f docker-compose.prod.yml up --build -d

backend: env up migrate
	cd backend && poetry run uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && NUXT_PUBLIC_API_BASE=http://localhost:8000 npm run dev

dev:
	@echo "Run in two terminals:"
	@echo "  make backend"
	@echo "  make frontend"
	@echo ""
	@echo "App:  http://localhost:3000"
	@echo "API:  http://localhost:8000/docs"

test: test-backend test-frontend

test-backend: install-backend up migrate
	cd backend && poetry run pytest -v

test-frontend: install-frontend
	cd frontend && npm test

lint:
	cd backend && poetry run ruff check .
	cd backend && poetry run ruff format --check .

lint-fix:
	cd backend && poetry run ruff check --fix .
	cd backend && poetry run ruff format .

clean:
	rm -rf frontend/node_modules frontend/.nuxt frontend/.output
	rm -rf backend/.venv
	find backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find backend -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
