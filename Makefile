.PHONY: install dev edge agent test lint format check smoke compose-up compose-down

install:
	python -m pip install -e "./agent[dev]"

dev:
	python -m uvicorn nexus_agent.api:app --app-dir agent --reload --host 127.0.0.1 --port 8000

edge:
	cargo run

agent:
	python -m uvicorn nexus_agent.api:app --app-dir agent --host 127.0.0.1 --port 8000

test:
	python -m pytest agent/tests -q

lint:
	ruff check agent

format:
	ruff format agent

check: lint
	cargo check
	python -m compileall -q agent

smoke:
	python agent/tests/smoke.py

compose-up:
	docker compose up --build

compose-down:
	docker compose down
