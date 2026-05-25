"""``archtool graph`` — visualise the dependency graph."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.tree import Tree

console = Console()


def _find_custom_layers(root: Path) -> Path | None:
    for candidate in (
        root / "app" / "archtool_conf" / "custom_layers.py",
        root / "archtool_conf" / "custom_layers.py",
        root / "app" / "custom_layers.py",
    ):
        if candidate.exists():
            return candidate
    return None


def _load_apps(path: Path):  # type: ignore[return]
    spec = importlib.util.spec_from_file_location("_archtool_conf", path)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return getattr(mod, "APPS", None)


@click.command()
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option(
    "--format",
    "fmt",
    default="tree",
    type=click.Choice(["tree", "dot"]),
    help="Output format: rich tree (default) or Graphviz DOT",
)
def graph(project_root: str, fmt: str) -> None:
    """Show the component dependency graph.

    Use ``--format dot`` and pipe through Graphviz::

        archtool graph --format dot | dot -Tsvg > deps.svg
    """
    from archtool.dependency_injector import DependencyInjector
    from archtool.utils import get_dependencies, serialize_dep_key

    root = Path(project_root).resolve()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    layers_file = _find_custom_layers(root)
    if layers_file is None:
        console.print("[red]Error:[/red] custom_layers.py not found.")
        raise SystemExit(1)

    apps = _load_apps(layers_file)
    if apps is None:
        raise SystemExit(1)

    try:
        injector = DependencyInjector(modules_list=apps, project_root=root)
        injector.inject()
    except Exception as exc:
        console.print(f"[red]Assembly failed:[/red] {exc}")
        raise SystemExit(1)

    # build edges: instance → [dependency instances]
    edges: list[tuple[str, str]] = []
    for key, instance in injector._dependencies.items():
        cls_name = type(instance).__name__
        for dep in get_dependencies(instance):
            dep_inst = injector._dependencies.get(dep.asked)
            dep_name = type(dep_inst).__name__ if dep_inst else dep.asked.split(".")[-1]
            edges.append((cls_name, dep_name))

    if fmt == "dot":
        lines = ["digraph archtool {", '    rankdir="LR";']
        for src, dst in edges:
            lines.append(f'    "{src}" -> "{dst}";')
        lines.append("}")
        click.echo("\n".join(lines))
        return

    # rich tree grouped by component
    tree = Tree("[bold]archtool dependency graph[/bold]")
    nodes: dict[str, Tree] = {}

    for key, instance in injector._dependencies.items():
        cls_name = type(instance).__name__
        if cls_name not in nodes:
            nodes[cls_name] = tree.add(f"[cyan]{cls_name}[/cyan]")

    for src, dst in edges:
        if src in nodes:
            nodes[src].add(f"[dim]→[/dim] {dst}")

    if not edges and injector._dependencies:
        for key, instance in injector._dependencies.items():
            tree.add(f"[cyan]{type(instance).__name__}[/cyan] [dim](no deps)[/dim]")

    console.print(tree)
