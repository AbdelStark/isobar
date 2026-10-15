.PHONY: setup check test build serve

setup:
	cd web && npm ci
	cd web && npm run build
	uv sync --locked

check:
	uv lock --check
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy src/isobar
	uv run pytest
	cd web && npm test
	cd web && npm run build

test:
	uv run pytest

build:
	cd web && npm run build
	uv build

serve:
	uv run isobar serve
