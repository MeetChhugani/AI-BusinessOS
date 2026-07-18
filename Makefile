.PHONY: up down build restart logs ps test migrate seed clean shell-backend shell-frontend

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

restart:
	docker compose down && docker compose up -d

logs:
	docker compose logs -f

ps:
	docker compose ps

test:
	docker compose exec -T backend pytest --cov=app --cov-report=term-missing app/tests

migrate:
	docker compose exec -T backend alembic upgrade head

seed:
	docker compose exec -T backend python seed.py

clean:
	docker compose down -v
	rm -rf backend/__pycache__ backend/app/__pycache__
	rm -rf backend/.pytest_cache backend/.coverage

shell-backend:
	docker compose exec backend bash

shell-frontend:
	docker compose exec frontend sh
