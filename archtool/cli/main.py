"""archtool CLI root group."""

from __future__ import annotations

import click

from archtool.cli.init_cmd import init
from archtool.cli.add_module_cmd import add_module
from archtool.cli.validate_cmd import validate
from archtool.cli.graph_cmd import graph


@click.group()
@click.version_option(package_name="archtool")
def cli() -> None:
    """archtool — dependency injection and architecture enforcement for Python."""


cli.add_command(init)
cli.add_command(add_module, name="add-module")
cli.add_command(validate)
cli.add_command(graph)
