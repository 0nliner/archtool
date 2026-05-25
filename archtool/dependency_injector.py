"""DependencyInjector — the main entry point for archtool DI assembly."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TypeVar

from archtool.exceptions import DependencyDuplicate, DependencyDoesNotRegistred, TopLevelLayerUsingException
from archtool.interfaces import DependencyInjectorInterface
from archtool.layers.default_layers import default_layers
from archtool.layers.di_basic_layer import Layer
from archtool.components.default_component import ComponentPattern
from archtool.global_types import AppModules, ContainerT, DEPENDENCY_KEY
from archtool.utils import (
    get_all_interfaces_and_realizations,
    get_dependencies,
    get_project_root,
    serialize_dep_key,
    set_project_root,
)

# Library-level logger — NullHandler so we never pollute host app logs
_lib_logger = logging.getLogger("archtool")
_lib_logger.addHandler(logging.NullHandler())

T = TypeVar("T")


class DependencyInjector(DependencyInjectorInterface):
    """Assembles and wires all DI components registered in *modules_list*.

    :param modules_list: Bounded-context modules to scan
                         (see :class:`~archtool.global_types.AppModule`).
    :param layers: Layer definitions. Defaults to the four standard layers
                   (Infrastructure → Domain → Application → Presentation).
    :param project_root: Absolute path to the project root directory.
                         When ``None``, archtool walks up from ``cwd`` looking
                         for ``pyproject.toml`` / ``.git`` / ``setup.cfg``.
                         Pass this explicitly from entrypoints to avoid any
                         ``sys.path`` manipulation.
    :param verbose: Enable archtool's own debug logging to *stderr*.
                    Defaults to ``False``; overrideable with the env-var
                    ``ARCHTOOL_VERBOSE=1``.
    """

    def __init__(
        self,
        modules_list: AppModules,
        layers: list[type[Layer]] | None = None,
        project_root: Path | None = None,
        verbose: bool | None = None,
        enforce_layers: bool = True,
    ) -> None:
        # ── logging ──────────────────────────────────────────────────────────
        if verbose is None:
            verbose = os.getenv("ARCHTOOL_VERBOSE", "0") == "1"

        if verbose:
            if not any(
                isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)
                for h in _lib_logger.handlers
            ):
                _handler = logging.StreamHandler()
                _handler.setFormatter(
                    logging.Formatter("[archtool] %(levelname)s %(message)s")
                )
                _lib_logger.addHandler(_handler)
            _lib_logger.setLevel(logging.DEBUG)

        # ── project root ─────────────────────────────────────────────────────
        root = project_root or get_project_root()
        set_project_root(root)
        _lib_logger.debug("project_root = %s", root)

        # ── layers ──────────────────────────────────────────────────────────
        self.modules_list = modules_list
        self.dependencies: dict[str, object] = {}
        self._allowed_nested: dict[str, bool] = {}
        self._enforce_layers = enforce_layers

        raw_layers = layers if layers is not None else default_layers
        self.layers: list[Layer] = [layer() for layer in raw_layers]

        _lib_logger.debug("registered modules: %s", [m.import_path for m in modules_list])

    # ── Public API ──────────────────────────────────────────────────────────

    def inject(self) -> None:
        """Scan all modules, instantiate components, and wire dependencies.

        Call this once after constructing the injector.

        **Pass 1** — discovery: each layer is scanned for interface/implementation
        pairs; concretions are instantiated and registered.

        **Between passes** — if ``enforce_layers=True``, the dependency graph is
        checked for upward references (e.g. a service depending on a controller).
        A violation raises :exc:`~archtool.exceptions.TopLevelLayerUsingException`
        immediately, before any ``setattr`` is called.

        **Pass 2** — injection: class-level annotations are resolved and
        ``setattr`` is called on each registered instance.
        """
        _lib_logger.info("starting injection (%d modules)", len(self.modules_list))

        # _component_to_layer maps serialised interface key → Layer instance.
        # Built during pass 1; used for layer enforcement between the two passes.
        self._component_to_layer: dict[str, Layer] = {}

        # ── pass 1: discover and register ────────────────────────────────────
        for layer in self.layers:
            if not isinstance(layer, Layer):
                continue
            for component_pattern in layer.component_groups:
                modules_to_use = self._exclude_ignored(component_pattern)
                _lib_logger.debug(
                    "layer component '%s': scanning %d modules",
                    component_pattern.module_name_regex,
                    len(modules_to_use),
                )
                pairs = get_all_interfaces_and_realizations(
                    app_modules=modules_to_use,
                    name_pattern=component_pattern.module_name_regex,
                    superclass=component_pattern.superclass,
                )
                for iface, impl_class in pairs.items():
                    serialised = serialize_dep_key(iface)
                    if serialised in self.dependencies:
                        _lib_logger.debug(
                            "skip %s — already manually registered", iface.__name__
                        )
                        continue
                    instance = impl_class()
                    self.register(key=iface, value=instance)
                    self._component_to_layer[serialised] = layer
                    _lib_logger.debug(
                        "registered %s → %s (layer: %s)",
                        iface.__name__,
                        impl_class.__name__,
                        type(layer).__name__,
                    )

        # ── layer enforcement ─────────────────────────────────────────────────
        if self._enforce_layers:
            self._check_layer_violations()

        # ── pass 2: inject dependencies into every registered instance ────────
        for key, instance in self.dependencies.items():
            if self._allowed_nested.get(key, True):
                self._inject_into(instance)

        _lib_logger.info("injection complete (%d components)", len(self.dependencies))

    def get_dependency(self, key: type[T] | str) -> T:
        """Retrieve a registered dependency by its interface class or serialised key.

        :param key: Interface class (e.g. ``UserServiceABC``) or serialised
                    string key.
        :raises DependencyDoesNotRegistred: The dependency is not registered.
        """
        if isinstance(key, str):
            serialised = key
        else:
            serialised = serialize_dep_key(key)
        return self._get(serialised)  # type: ignore[return-value]

    # ── Private helpers ─────────────────────────────────────────────────────

    def _exclude_ignored(self, component_pattern: ComponentPattern) -> AppModules:
        return [m for m in self.modules_list if component_pattern not in m.ignore]

    def register(
        self,
        key: DEPENDENCY_KEY,
        value: object,
        inject_into: bool = True,
    ) -> None:
        """Manually register a dependency.

        Use this to register instances that archtool cannot discover
        automatically — e.g. async resources initialised before startup,
        third-party objects, or conditionally-created instances.

        :param key: Interface class used as the lookup key (same class you
                    would declare in a class-level annotation).
        :param value: The instance to register.
        :param inject_into: When ``True`` (default), archtool will also
                            inject *this* instance's own dependencies in the
                            second pass.
        :raises DependencyDuplicate: A different instance is already registered
                                     for *key*.
        """
        serialised = serialize_dep_key(key)
        if serialised in self.dependencies:
            if self.dependencies[serialised] is value:
                return
            raise DependencyDuplicate(serialised)
        self.dependencies[serialised] = value
        self._allowed_nested[serialised] = inject_into
        _lib_logger.debug("manually registered %s → %s", serialised, type(value).__name__)

    # backward-compat alias
    _register = register

    def _get_allowed_layer_types(self, layer: Layer) -> set[type]:
        """Return the set of layer *types* that *layer* is allowed to depend on.

        Includes the layer itself (same-layer dependencies are always permitted)
        and every layer reachable by walking the ``depends_on`` chain downward.
        """
        allowed: set[type] = {type(layer)}
        current: type[Layer] | None = type(layer)
        while current is not None:
            dep: type[Layer] | None = getattr(current, "depends_on", None)
            if dep is None or not isinstance(dep, type):
                break
            allowed.add(dep)
            current = dep
        return allowed

    def _check_layer_violations(self) -> None:
        """Raise TopLevelLayerUsingException if any auto-discovered component
        depends on a component from a layer it is not allowed to use.

        Only auto-discovered components are checked; manually pre-registered
        dependencies (not present in ``_component_to_layer``) are skipped
        because their layer membership is unknown.
        """
        for serialised_key, instance in self.dependencies.items():
            container_layer = self._component_to_layer.get(serialised_key)
            if container_layer is None:
                # manually registered — no layer to check against
                continue

            allowed = self._get_allowed_layer_types(container_layer)

            for dep in get_dependencies(instance):
                dep_layer = self._component_to_layer.get(dep.asked)
                if dep_layer is None:
                    # dependency is manually registered or from unknown source — skip
                    continue

                if type(dep_layer) not in allowed:
                    raise TopLevelLayerUsingException(
                        container_class=type(instance).__name__,
                        container_layer=type(container_layer).__name__,
                        dependency_name=dep.asked.split(".")[-1],
                        dependency_layer=type(dep_layer).__name__,
                    )

    def _inject_into(self, container: ContainerT) -> None:
        for dep in get_dependencies(container):
            dependency = self._get(dep.asked)
            setattr(container, dep.name, dependency)
            _lib_logger.debug(
                "injected %s.%s ← %s",
                type(container).__name__,
                dep.name,
                type(dependency).__name__,
            )

    def _get(self, key: str) -> object:
        try:
            return self.dependencies[key]
        except KeyError:
            registered = list(self.dependencies.keys())
            raise DependencyDoesNotRegistred(key, registered) from None
