"""``archtool add-module <name>`` — add a domain module to an existing project."""

from __future__ import annotations

import re
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

console = Console()

# ── templates ────────────────────────────────────────────────────────────────

_INTERFACES = """\
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

_SERVICES = """\
from .interfaces import {pascal}ServiceABC, {pascal}RepoABC


class {pascal}Service({pascal}ServiceABC):
    repo: {pascal}RepoABC

    def example_action(self) -> str:
        data = self.repo.fetch_data()
        return f"processed {{len(data)}} items"
"""

_REPOS = """\
from .interfaces import {pascal}RepoABC


class {pascal}Repo({pascal}RepoABC):
    def fetch_data(self) -> list[str]:
        return []
"""

_TEST_CONFTEST = """\
import pytest
from unittest.mock import MagicMock

from app.{dotted}.interfaces import {pascal}ServiceABC, {pascal}RepoABC
from app.{dotted}.services import {pascal}Service


@pytest.fixture
def repo():
    return MagicMock(spec={pascal}RepoABC)


@pytest.fixture
def service(repo):
    s = {pascal}Service()
    s.repo = repo
    return s
"""

_TEST_SERVICES = """\
class Test{pascal}Service:
    def test_example_action(self, service):
        result = service.example_action()
        assert isinstance(result, str)
"""


def _to_pascal(name: str) -> str:
    return "".join(word.capitalize() for word in re.split(r"[._\-\s]+", name))


def _write(path: Path, content: str) -> None:
    if path.exists():
        console.print(f"  [yellow]~[/yellow] Skipped {path} (already exists)")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    console.print(f"  [green]✓[/green] Created {path}")


def _find_custom_layers(project_root: Path) -> Path | None:
    for candidate in (
        project_root / "app" / "archtool_conf" / "custom_layers.py",
        project_root / "archtool_conf" / "custom_layers.py",
        project_root / "app" / "custom_layers.py",
    ):
        if candidate.exists():
            return candidate
    return None


def _register_in_apps(layers_file: Path, module_import_path: str) -> None:
    """Append AppModule(...) to the APPS list in custom_layers.py."""
    text = layers_file.read_text(encoding="utf-8")
    entry = f'    AppModule("{module_import_path}"),'

    if module_import_path in text:
        console.print(f"  [yellow]~[/yellow] '{module_import_path}' already in APPS — skipped")
        return

    # insert before the closing ] of APPS
    pattern = re.compile(r"(APPS\s*[:=][^[]*\[)(.*?)(\])", re.DOTALL)
    match = pattern.search(text)
    if match:
        new_text = text[: match.start(3)] + "\n" + entry + "\n" + text[match.start(3) :]
        layers_file.write_text(new_text, encoding="utf-8")
        console.print(
            f"  [green]✓[/green] Added AppModule('{module_import_path}') to {layers_file}"
        )
    else:
        console.print(
            f"  [red]✗[/red] Could not locate APPS list in {layers_file}. "
            f"Add manually: AppModule('{module_import_path}')"
        )


@click.command()
@click.argument("name")
@click.option(
    "--project-root",
    default=".",
    help="Project root directory (default: cwd)",
    type=click.Path(file_okay=False, exists=True),
)
def add_module(name: str, project_root: str) -> None:
    """Add a new domain module NAME to the project.

    NAME supports dot-notation for nested modules, e.g. ``payments.gateway``.
    The corresponding directory structure is created under ``app/``.
    """
    root = Path(project_root).resolve()
    dotted = name.replace("-", "_").replace("/", ".")
    parts = dotted.split(".")
    pascal = _to_pascal(parts[-1])

    module_path = root / "app" / Path(*parts)
    module_import = "app." + dotted

    console.print(
        Panel(
            f"[bold]Adding module [cyan]{name}[/cyan][/bold]",
            expand=False,
        )
    )

    _write(module_path / "__init__.py", "")
    _write(module_path / "interfaces.py", _INTERFACES.format(pascal=pascal))
    _write(module_path / "services.py", _SERVICES.format(pascal=pascal))
    _write(module_path / "repos.py", _REPOS.format(pascal=pascal))
    _write(module_path / "tests" / "__init__.py", "")
    _write(
        module_path / "tests" / "conftest.py",
        _TEST_CONFTEST.format(pascal=pascal, dotted=dotted),
    )
    _write(
        module_path / "tests" / "test_services.py",
        _TEST_SERVICES.format(pascal=pascal),
    )

    layers_file = _find_custom_layers(root)
    if layers_file:
        _register_in_apps(layers_file, module_import)
    else:
        console.print(
            f"  [yellow]![/yellow] custom_layers.py not found — add "
            f"AppModule('{module_import}') to APPS manually."
        )

    console.print()
    console.print(
        f"[green]Module '{name}' created.[/green] Run [bold]make validate-arch[/bold] to check assembly."
    )
