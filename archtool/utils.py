"""Core utilities: path resolution, module scanning, dependency extraction."""

from __future__ import annotations

import logging
import typing
from abc import ABCMeta
from inspect import getfile, getmro, isabstract, isclass
from importlib import import_module
from pathlib import Path
from re import sub
from typing import Callable

from archtool.exceptions import (
    CheckFailedException,
    MultipleRealizationsException,
    RealizationNotFound,
)
from archtool.global_types import (
    AppModule,
    AppModules,
    Dependency,
    DEPENDENCY_KEY,
    InterfaceT,
)

logger = logging.getLogger("archtool")

# ── Project root resolution ───────────────────────────────────────────────────

_project_root: Path | None = None


def set_project_root(root: Path) -> None:
    """Set the project root used for all import path resolution.

    Called once by :class:`~archtool.dependency_injector.DependencyInjector`
    during initialisation. Safe to call multiple times (e.g. in tests).
    """
    global _project_root
    _project_root = root.resolve()


def _detect_project_root() -> Path:
    """Walk up from cwd until a project marker is found."""
    markers = ("pyproject.toml", "setup.cfg", "setup.py", ".git")
    for path in [Path.cwd(), *Path.cwd().parents]:
        if any((path / m).exists() for m in markers):
            return path
    return Path.cwd()


def get_project_root() -> Path:
    """Return the active project root (set or auto-detected)."""
    return _project_root if _project_root is not None else _detect_project_root()


# ── Import path resolution ─────────────────────────────────────────────────

def resolve_import_path(obj: object | str) -> str:
    """Return the canonical dotted import path for a class or a module string.

    The path is always prefixed with the project root directory name so that
    all resolved paths are comparable regardless of whether the input was a
    class object or a module string.

    Examples::

        # project root: /home/user/myproject
        resolve_import_path(MyService)
        # → "myproject.app.users.services"

        resolve_import_path("app.users.services")
        # → "myproject.app.users.services"
    """
    root = get_project_root()
    root_name = root.name

    if isinstance(obj, str):
        # already has project root prefix — return as-is
        if obj == root_name or obj.startswith(root_name + "."):
            return obj
        return f"{root_name}.{obj}"

    # obj is a class or module — resolve via filesystem path
    try:
        file_path = Path(getfile(obj)).resolve()
    except (TypeError, OSError) as exc:
        raise TypeError(
            f"Cannot determine source file for {obj!r}: {exc}"
        ) from exc

    try:
        relative = file_path.relative_to(root)
    except ValueError:
        # file lives outside the project root (e.g. third-party library)
        raise TypeError(
            f"Object {obj!r} is defined in {file_path}, which is outside "
            f"the project root {root}. Only project-local classes can be "
            f"used as DI components."
        )

    parts = (root_name,) + relative.with_suffix("").parts
    return ".".join(parts)


# ── Helpers ────────────────────────────────────────────────────────────────

def string_to_snake_case(string: str) -> str:
    string = sub('[<>]', '', string)
    return '_'.join(
        sub('([A-Z][a-z]+)', r' \1',
        sub('([A-Z]+)', r' \1',
        string.replace('-', ' '))).split()).lower()


def inherits_from(child: type, parent_name: str) -> bool:
    if isclass(child):
        return parent_name in [c.__name__ for c in getmro(child)[1:]]
    return False


def check_is_not_interface(obj: type) -> bool:
    return not isabstract(obj)


def serialize_dep_key(key: DEPENDENCY_KEY) -> str:
    return f"{resolve_import_path(key.__module__)}.{key.__name__}"


# ── Dependency extraction ─────────────────────────────────────────────────

def get_dependencies(container: object) -> list[Dependency]:
    """Extract DI dependencies from class-level annotations.

    Uses :func:`typing.get_type_hints` so that ``from __future__ import
    annotations`` does not break resolution — all string annotations are
    resolved to actual types before inspection.
    """
    cls = type(container) if not isinstance(container, type) else container
    own_annotations: dict[str, object] = vars(cls).get("__annotations__", {})
    if not own_annotations:
        return []

    # Resolve string annotations produced by `from __future__ import annotations`
    try:
        resolved = typing.get_type_hints(cls)
    except Exception as exc:
        logger.debug("get_type_hints failed for %s (%s), using raw annotations", cls, exc)
        resolved = {}

    dependencies: list[Dependency] = []
    for name in own_annotations:
        # skip private attributes (e.g. _active, __state)
        if name.startswith("_"):
            continue

        dep = resolved.get(name, own_annotations[name])
        if isinstance(dep, (type, ABCMeta)):
            dep_key = serialize_dep_key(dep)
            dependencies.append(Dependency(name=name, asked=dep_key))

    return dependencies


# ── Module scanning ────────────────────────────────────────────────────────

def get_subclasses_from_module(
    module_path: str,
    superclass: type,
    extra_checks: list[Callable[[type], bool]] | None = None,
) -> list[type]:
    """Return non-abstract subclasses of *superclass* **defined** in *module_path*.

    Imported classes (defined elsewhere) are excluded via path comparison.
    Nested subpackages of *module_path* are included — a class defined in
    ``app.foo.bar.services`` is considered part of module ``app.foo.bar``.
    """
    if extra_checks is None:
        extra_checks = []

    module_obj = import_module(module_path)
    module_absolute = resolve_import_path(module_path)
    results: list[type] = []

    for key, obj in vars(module_obj).items():
        if not isclass(obj) or key.startswith("__"):
            continue
        if not inherits_from(child=obj, parent_name=superclass.__name__):
            continue
        if obj is superclass:
            continue

        try:
            obj_path = resolve_import_path(obj)
        except TypeError:
            # built-ins, C extensions, or library classes outside project root
            continue

        # belongs to this module or any of its subpackages
        is_in_module = (
            obj_path == module_absolute
            or obj_path.startswith(module_absolute + ".")
        )
        if not is_in_module:
            logger.debug(
                "skip %s: defined in %s, not in %s",
                obj.__name__, obj_path, module_absolute,
            )
            continue

        try:
            for check in extra_checks:
                if not check(obj):
                    raise CheckFailedException(check)
        except CheckFailedException:
            continue

        results.append(obj)

    return results


def get_class_instances_from_module(
    module_path: str,
    cls: type,
    extra_checks: list[Callable[[object], bool]] | None = None,
) -> list[object]:
    """Return instances of *cls* found in *module_path*."""
    if extra_checks is None:
        extra_checks = []

    module_obj = import_module(module_path)
    results: list[object] = []
    for obj in vars(module_obj).values():
        if type(obj) is not cls:
            continue
        try:
            for check in extra_checks:
                if not check(obj):
                    raise CheckFailedException(check)
        except CheckFailedException:
            continue
        results.append(obj)
    return results


# ── Interface / realization discovery ─────────────────────────────────────

def get_module_interfaces(module: AppModule, superclass: type) -> list[InterfaceT]:
    """Return all abstract subclasses of *superclass* from *module*.interfaces."""
    layer_module_path = f"{module.import_path}.interfaces"
    return get_subclasses_from_module(
        module_path=layer_module_path,
        superclass=superclass,
        extra_checks=[isabstract],
    )


def get_interface_realization(
    module: AppModule,
    name_pattern: str,
    interface: type,
) -> type:
    """Return the single concrete realization of *interface* in *module*.*name_pattern*.

    :raises MultipleRealizationsException: more than one realization found.
    :raises RealizationNotFound: no realization found.
    """
    module_path = f"{module.import_path}.{name_pattern}"
    realizations = get_subclasses_from_module(
        module_path=module_path,
        superclass=interface,
        extra_checks=[check_is_not_interface],
    )

    if len(realizations) > 1:
        names = [r.__name__ for r in realizations]
        raise MultipleRealizationsException(
            f"Multiple realizations of {interface.__name__!r} found in "
            f"'{module_path}': {names}. Each interface must have exactly one "
            f"concrete implementation per module."
        )
    if not realizations:
        raise RealizationNotFound(
            f"No realization of {interface.__name__!r} found in '{module_path}'. "
            f"Create a concrete class that inherits from {interface.__name__} in "
            f"that file."
        )
    return realizations[0]


def get_all_interfaces_and_realizations(
    app_modules: AppModules,
    superclass: type,
    name_pattern: str,
) -> dict[type, type]:
    """Return ``{interface_class: realization_class}`` for every module."""
    result: dict[type, type] = {}
    for module in app_modules:
        interfaces = get_module_interfaces(module=module, superclass=superclass)
        for interface in interfaces:
            realization = get_interface_realization(
                module=module,
                interface=interface,
                name_pattern=name_pattern,
            )
            result[interface] = realization
    return result
