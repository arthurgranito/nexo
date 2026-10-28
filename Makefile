.PHONY: up down migrate seed test lint
up:
	docker compose up --build -d
down:
	docker compose down
migrate:
	docker compose run --rm migrate
seed:
	docker compose --profile tools run --rm seed
test:
	cd backend && python -m pytest -q
lint:
	cd backend && ruff check .
	cd frontend && npm run typecheck
