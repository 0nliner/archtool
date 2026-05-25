.PHONY: install install-dev test lint typecheck fmt build docs docs-serve clean

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest --tb=short -q

test-cov:
	pytest --cov=archtool --cov-report=term-missing -q

lint:
	ruff check archtool tests

fmt:
	ruff format archtool tests

typecheck:
	mypy archtool --ignore-missing-imports

build:
	pip install build
	python -m build

docs:
	pip install -e ".[docs]"
	mkdocs gh-deploy --force

docs-serve:
	pip install -e ".[docs]"
	mkdocs serve

clean:
	rm -rf dist/ build/ *.egg-info .coverage htmlcov/ .mypy_cache/ .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
