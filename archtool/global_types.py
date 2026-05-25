"""Public types used across archtool."""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# Generic type aliases
ContainerT = Any
InterfaceT = Any  # ABC subclass


@dataclass
class Dependency:
    """A single DI dependency: the attribute name and the serialised key to look up.

    :param name: Attribute name on the container class (e.g. ``"repo"``).
    :param asked: Serialised dotted path to the interface class
                  (e.g. ``"myproject.app.users.interfaces.UserRepoABC"``).
    """

    name: str
    asked: str


DependeciesT = list[Dependency]

DEPENDENCY_KEY = Any  # interface class, serialised string, or object


@dataclass(repr=True)
class AppModule:
    """Descriptor for a single bounded-context module registered with archtool.

    :param import_path: Dotted Python import path relative to the project root
                        (e.g. ``"app.users"`` or ``"app.payments.gateway"``).
    :param ignore: Layer component patterns that should be skipped for this module.
    """

    import_path: str
    ignore: list[Any] = field(default_factory=list)

    def validate(self) -> list[str]:
        """Check that the module exists and has the expected structure.

        :return: List of problem strings. An empty list means the module is valid.
        """
        problems: list[str] = []
        spec = importlib.util.find_spec(self.import_path)
        if spec is None:
            problems.append(f"Module '{self.import_path}' not found on sys.path")
            return problems

        # For packages, check that interfaces.py exists
        if spec.submodule_search_locations is not None:
            pkg_path = Path(next(iter(spec.submodule_search_locations)))
            if not (pkg_path / "interfaces.py").exists():
                problems.append(f"Missing interfaces.py in {pkg_path}")

        return problems

    @property
    def absolute_import_path(self) -> str:
        """Return the import path as-is (kept for backward compatibility)."""
        return self.import_path


AppModules = list[AppModule]
