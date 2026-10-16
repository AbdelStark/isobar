.PHONY: setup check test build serve web-build browser-setup check-browser check-package verify

setup:
	cd web && npm ci
	cd web && npm run build
	uv sync --locked

check: web-build
	uv lock --check
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy src/isobar
	uv run pytest
	cd web && npm test

test:
	uv run pytest

web-build:
	cd web && npm run build

build: web-build
	uv build

browser-setup:
	cd web && npx playwright install --with-deps chromium

check-browser: web-build
	cd web && npm run test:browser

check-package: web-build
	uv run python scripts/check_package.py

verify: check check-browser check-package

serve:
	uv run isobar serve
