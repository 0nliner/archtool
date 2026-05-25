"""``archtool validate`` — check DI assembly without starting the server."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

console = Console()


def _load_apps(custom_layers_path: Path) -> list | None:
    """Import custom_layers.py and return the APPS list."""
    spec = importlib.util.spec_from_file_location("_archtool_conf", custom_layers_path)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    except Exception as exc:
        console.print(f"[red]Error loading {custom_layers_path}: {exc}[/red]")
        return None
    return getattr(mod, "APPS", None)


def _find_custom_layers(root: Path) -> Path | None:
    for candidate in (
        root / "app" / "archtool_conf" / "custom_layers.py",
        root / "archtool_conf" / "custom_layers.py",
        root / "app" / "custom_layers.py",
    ):
        if candidate.exists():
            return candidate
    return None


@click.command()
@click.option(
    "--project-root",
    default=".",
    help="Project root (default: cwd)",
    type=click.Path(file_okay=False),
)
@click.option("--verbose", "-v", is_flag=True, help="Show DI debug output")
def validate(project_root: str, verbose: bool) -> None:
    """Validate DI assembly: scan all modules and report missing/duplicate components.

    Exits with code 1 if any errors are found.
    """
    from archtool.dependency_injector import DependencyInjector
    from archtool.exceptions import (
        DependencyDoesNotRegistred,
        MultipleRealizationsException,
        RealizationNotFound,
    )
    from archtool.global_types import AppModule

    root = Path(project_root).resolve()

    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    layers_file = _find_custom_layers(root)
    if layers_file is None:
        console.print("[red]Error:[/red] Could not find custom_layers.py.")
        console.print("Expected at: app/archtool_conf/custom_layers.py")
        raise SystemExit(1)

    apps: list[AppModule] | None = _load_apps(layers_file)
    if apps is None:
        console.print("[red]Error:[/red] APPS not found in custom_layers.py.")
        raise SystemExit(1)

    console.print(f"Scanning [bold]{len(apps)}[/bold] modules...\n")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Module", style="cyan", no_wrap=True)
    table.add_column("Status", no_wrap=True)
    table.add_column("Details")

    errors: list[str] = []

    for module in apps:
        problems = module.validate()
        if problems:
            for p in problems:
                table.add_row(module.import_path, "[red]✗ error[/red]", p)
                errors.append(p)
            continue

        try:
            injector = DependencyInjector(
                modules_list=[module],
                project_root=root,
                verbose=verbose,
            )
            injector.inject()
            count = len(injector._dependencies)
            table.add_row(
                module.import_path,
                "[green]✓ ok[/green]",
                f"{count} component(s)",
            )
        except RealizationNotFound as exc:
            msg = str(exc)
            table.add_row(module.import_path, "[red]✗ missing[/red]", msg)
            errors.append(msg)
        except MultipleRealizationsException as exc:
            msg = str(exc)
            table.add_row(module.import_path, "[red]✗ duplicate[/red]", msg)
            errors.append(msg)
        except DependencyDoesNotRegistred as exc:
            msg = str(exc).split("\n")[0]
            table.add_row(module.import_path, "[yellow]! warning[/yellow]", msg)
        except Exception as exc:
            msg = f"{type(exc).__name__}: {exc}"
            table.add_row(module.import_path, "[red]✗ error[/red]", msg)
            errors.append(msg)

    console.print(table)
    console.print()

    if errors:
        console.print(f"[red]Errors: {len(errors)}[/red]")
        raise SystemExit(1)
    else:
        console.print("[green]All modules OK.[/green]")
