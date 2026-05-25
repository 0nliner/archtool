"""``archtool init <name>`` — scaffold a new project."""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

console = Console()

# ── file templates ──────────────────────────────────────────────────────────

_PYPROJECT = """\
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{name}"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "archtool",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "ruff>=0.4",
    "mypy>=1.10",
]

[tool.pytest.ini_options]
testpaths = ["."]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
norecursedirs = [".git", ".venv", "build", "dist", "__pycache__"]
addopts = "-q --tb=short"
"""

_GITIGNORE = """\
.venv/
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.mypy_cache/
.ruff_cache/
dist/
build/
*.egg-info/
.env
"""

_MAKEFILE = """\
.DEFAULT_GOAL := help

.PHONY: help install dev test test-domain lint format typecheck \\
        migrate migrate-create migrate-rollback run run-dev \\
        validate-arch docker-build docker-up docker-down clean

install:        ## Install production dependencies
\tuv sync --frozen --no-dev

dev:            ## Install dev dependencies
\tuv sync --group dev

test:           ## Run all tests
\tuv run pytest -q

test-domain:    ## Run tests for a single domain: make test-domain d=users
\tuv run pytest app/$(d)/tests/ -v

test-cov:       ## Run tests with coverage report
\tuv run pytest --cov=app --cov-report=term-missing -q

lint:           ## Lint with ruff
\tuv run ruff check .

format:         ## Auto-format with ruff
\tuv run ruff format .

typecheck:      ## Type-check with mypy
\tuv run mypy app

validate-arch:  ## Validate DI assembly without starting the server
\tuv run archtool validate

migrate:        ## Apply all migrations
\tuv run alembic upgrade head

migrate-create: ## Create a migration: make migrate-create m="add users table"
\tuv run alembic revision --autogenerate -m "$(m)"

migrate-rollback: ## Roll back the last migration
\tuv run alembic downgrade -1

migrate-history: ## Show migration history
\tuv run alembic history --verbose

run:            ## Start production server
\tuv run python entrypoints/run.py

run-dev:        ## Start dev server with hot reload
\tuv run uvicorn entrypoints.asgi:app --reload --host 0.0.0.0 --port 8000

docker-build:   ## Build Docker image
\tdocker compose build

docker-up:      ## Start all services
\tdocker compose up -d

docker-down:    ## Stop all services
\tdocker compose down

docker-logs:    ## Tail application logs
\tdocker compose logs -f app

clean:          ## Remove caches and build artifacts
\tfind . -type d -name __pycache__ -exec rm -rf {{}} + 2>/dev/null; \\
\tfind . -type d -name .pytest_cache -exec rm -rf {{}} + 2>/dev/null; \\
\tfind . -type d -name .mypy_cache  -exec rm -rf {{}} + 2>/dev/null; \\
\tfind . -type d -name .ruff_cache  -exec rm -rf {{}} + 2>/dev/null; \\
\trm -rf dist/ build/ *.egg-info/

help:           ## Show this help
\t@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \\
\t  | awk 'BEGIN {{FS = ":.*?## "}}; {{printf "  \\033[36m%-20s\\033[0m %s\\n", $$1, $$2}}'
"""

_DOCKERFILE = """\
# ── build stage ──────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev --no-editable

# ── runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \\
    PYTHONUNBUFFERED=1 \\
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY . .

EXPOSE 8000

CMD ["python", "entrypoints/run.py"]
"""

_DOCKER_COMPOSE = """\
services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file: .env.example
    volumes:
      - .:/app
    command: uvicorn entrypoints.asgi:app --reload --host 0.0.0.0

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ${DB_NAME:-appdb}
      POSTGRES_USER: ${DB_USER:-app}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-secret}
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
"""

_DOCKERIGNORE = """\
.git
.venv
__pycache__
*.pyc
*.pyo
.pytest_cache
.mypy_cache
.ruff_cache
dist/
build/
*.egg-info/
.env
"""

_ENV_EXAMPLE = """\
DB_NAME=appdb
DB_USER=app
DB_PASSWORD=secret
DB_HOST=db
DB_PORT=5432
"""

_CUSTOM_LAYERS = """\
from archtool.global_types import AppModule, AppModules
from archtool.layers.default_layers import (
    InfrastructureLayer,
    DomainLayer,
    ApplicationLayer,
)

app_layers = frozenset([
    InfrastructureLayer,
    DomainLayer,
    ApplicationLayer,
])

APPS: AppModules = [
    AppModule("app.example_module"),
]
"""

_BUNDLE = """\
from pathlib import Path

from archtool.dependency_injector import DependencyInjector
from archtool.layers.default_layers import default_layers

from app.archtool_conf.custom_layers import APPS, app_layers

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def create_injector(verbose: bool = False) -> DependencyInjector:
    injector = DependencyInjector(
        modules_list=APPS,
        layers=list(app_layers),
        project_root=PROJECT_ROOT,
        verbose=verbose,
    )
    injector.inject()
    return injector
"""

_ENTRYPOINT_RUN = """\
\"\"\"Application entrypoint — no sys.path manipulation needed.\"\"\"

from app.archtool_conf.bundle import create_injector

if __name__ == "__main__":
    injector = create_injector(verbose=False)
    print("DI assembled successfully.")
    print(f"Registered components: {len(injector._dependencies)}")
"""

_MODULE_INIT = ""
_MODULE_INTERFACES = """\
from abc import abstractmethod

from archtool.layers.default_layer_interfaces import ABCService, ABCRepo


class {pascal}ServiceABC(ABCService):
    @abstractmethod
    def example_action(self) -> str:
        ...


class {pascal}RepoABC(ABCRepo):
    @abstractmethod
    def fetch_data(self) -> list[str]:
        ...
"""

_MODULE_SERVICES = """\
from .interfaces import {pascal}ServiceABC, {pascal}RepoABC


class {pascal}Service({pascal}ServiceABC):
    repo: {pascal}RepoABC

    def example_action(self) -> str:
        data = self.repo.fetch_data()
        return f"processed {{len(data)}} items"
"""

_MODULE_REPOS = """\
from .interfaces import {pascal}RepoABC


class {pascal}Repo({pascal}RepoABC):
    def fetch_data(self) -> list[str]:
        return ["item1", "item2"]
"""

_MODULE_TEST_CONFTEST = """\
import pytest
from unittest.mock import MagicMock

from app.{snake}.interfaces import {pascal}ServiceABC, {pascal}RepoABC
from app.{snake}.services import {pascal}Service


@pytest.fixture
def repo():
    return MagicMock(spec={pascal}RepoABC)


@pytest.fixture
def service(repo):
    s = {pascal}Service()
    s.repo = repo
    return s
"""

_MODULE_TEST_SERVICES = """\
class Test{pascal}Service:
    def test_example_action(self, service):
        result = service.example_action()
        assert isinstance(result, str)
"""

_TESTS_ASSEMBLY = """\
\"\"\"Integration test: DI assembles without errors.\"\"\"

from pathlib import Path
from archtool.dependency_injector import DependencyInjector
from app.archtool_conf.custom_layers import APPS, app_layers

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_di_assembles():
    injector = DependencyInjector(
        modules_list=APPS,
        layers=list(app_layers),
        project_root=PROJECT_ROOT,
    )
    injector.inject()
    assert len(injector._dependencies) > 0
"""


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    console.print(f"  [green]✓[/green] Created {path}")


@click.command()
@click.argument("name")
@click.option("--path", default=".", help="Parent directory for the new project (default: cwd)")
def init(name: str, path: str) -> None:
    """Scaffold a new archtool project in a directory called NAME."""
    root = Path(path) / name
    if root.exists():
        console.print(f"[red]Error:[/red] '{root}' already exists.")
        raise SystemExit(1)

    console.print(Panel(f"[bold]Creating project [cyan]{name}[/cyan][/bold]", expand=False))

    pascal = name.replace("-", "_").replace(" ", "_").title().replace("_", "")
    snake = name.replace("-", "_").lower()

    module_path = root / "app" / "example_module"

    _write(root / "pyproject.toml", _PYPROJECT.format(name=name))
    _write(root / ".gitignore", _GITIGNORE)
    _write(root / "Makefile", _MAKEFILE)
    _write(root / "Dockerfile", _DOCKERFILE)
    _write(root / "docker-compose.yml", _DOCKER_COMPOSE)
    _write(root / ".dockerignore", _DOCKERIGNORE)
    _write(root / ".env.example", _ENV_EXAMPLE)

    # archtool conf
    _write(root / "app" / "__init__.py", "")
    _write(root / "app" / "archtool_conf" / "__init__.py", "")
    _write(root / "app" / "archtool_conf" / "custom_layers.py", _CUSTOM_LAYERS)
    _write(root / "app" / "archtool_conf" / "bundle.py", _BUNDLE)

    # example module
    _write(module_path / "__init__.py", _MODULE_INIT)
    _write(module_path / "interfaces.py", _MODULE_INTERFACES.format(pascal=pascal))
    _write(module_path / "services.py", _MODULE_SERVICES.format(pascal=pascal))
    _write(module_path / "repos.py", _MODULE_REPOS.format(pascal=pascal))
    _write(module_path / "tests" / "__init__.py", "")
    _write(
        module_path / "tests" / "conftest.py",
        _MODULE_TEST_CONFTEST.format(pascal=pascal, snake=snake),
    )
    _write(
        module_path / "tests" / "test_services.py",
        _MODULE_TEST_SERVICES.format(pascal=pascal),
    )

    # entrypoints
    _write(root / "entrypoints" / "__init__.py", "")
    _write(root / "entrypoints" / "run.py", _ENTRYPOINT_RUN)

    # global tests
    _write(root / "tests" / "__init__.py", "")
    _write(root / "tests" / "test_assembly.py", _TESTS_ASSEMBLY)

    console.print()
    console.print(
        Panel(
            f"[bold green]Project '{name}' created![/bold green]\n\n"
            f"Next steps:\n"
            f"  cd {name}\n"
            f"  uv sync --group dev\n"
            f"  make test\n"
            f"  make validate-arch",
            expand=False,
        )
    )
