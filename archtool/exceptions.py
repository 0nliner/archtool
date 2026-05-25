"""archtool exceptions."""

from __future__ import annotations


class ArchToolError(Exception):
    """Base class for all archtool exceptions."""


class CheckFailedException(ArchToolError):
    """A custom check function returned False for a candidate class."""


class UsedButIgnoredError(ArchToolError):
    """A module is used as a dependency but declared as ignored."""


class TopLevelLayerUsingException(ArchToolError):
    """A component depends on another component from a higher (disallowed) layer.

    archtool enforces that dependencies only flow *downward* in the layer
    hierarchy — e.g. a service (Domain) may depend on a repo (Infrastructure),
    but not on a controller (Application).
    """

    def __init__(
        self,
        container_class: str,
        container_layer: str,
        dependency_name: str,
        dependency_layer: str,
    ) -> None:
        super().__init__(
            f"Layer boundary violation detected at startup.\n\n"
            f"  '{container_class}' lives in {container_layer}\n"
            f"  but depends on '{dependency_name}' from {dependency_layer}.\n\n"
            f"{container_layer} is not allowed to depend on {dependency_layer}. "
            f"Dependencies must flow downward in the layer hierarchy. "
            f"If '{dependency_name}' is intentional, pre-register it via "
            f"injector.register() before inject() — manually registered "
            f"dependencies bypass layer checks."
        )


class DependencyDuplicate(ArchToolError):
    """An interface has been registered more than once in the DI container.

    This usually means two modules both define a concrete class that
    implements the same interface.
    """

    def __init__(self, key: str) -> None:
        super().__init__(
            f"Interface '{key}' is already registered in the DI container. "
            f"Each interface must have exactly one concrete implementation "
            f"across all registered modules."
        )


class DependencyDoesNotRegistred(ArchToolError):
    """A required dependency is not registered in the DI container.

    Check that the module owning the dependency's interface is listed in APPS,
    and that a concrete implementation exists in the corresponding layer file.
    """

    def __init__(self, key: str, registered: list[str] | None = None) -> None:
        hint = ""
        if registered:
            hint = "\n\nRegistered dependencies:\n" + "\n".join(f"  • {k}" for k in registered)
        super().__init__(f"Dependency '{key}' is not registered in the DI container.{hint}")


class MultipleRealizationsException(ArchToolError):
    """More than one concrete class implements the same interface in a module."""


class RealizationNotFound(ArchToolError):
    """No concrete implementation of an interface was found in the expected file."""


# backward-compat alias (typo in original)
RealizationNotFount = RealizationNotFound


class ModuleValidationError(ArchToolError):
    """An AppModule failed validation checks."""

    def __init__(self, module_path: str, problems: list[str]) -> None:
        problems_str = "\n".join(f"  • {p}" for p in problems)
        super().__init__(f"Module '{module_path}' failed validation:\n{problems_str}")


class AnnotationsNotResolvableError(ArchToolError):
    """Class annotations could not be resolved.

    Most likely cause: ``from __future__ import annotations`` combined with a
    forward reference that cannot be resolved at DI assembly time.
    """


class CircularDependencyError(ArchToolError):
    """A circular dependency was detected during DI assembly.

    archtool performs a topological sort before Pass 2 injection. If the
    dependency graph contains a cycle, assembly is aborted immediately.
    """

    def __init__(self, cycle: list[str]) -> None:
        path = " → ".join(c.split(".")[-1] for c in cycle)
        super().__init__(
            f"Circular dependency detected: {path}\n\n"
            f"Full keys: {cycle}\n\n"
            f"Break the cycle by introducing an interface that one side depends on, "
            f"or pre-register one of the components via injector.register() before inject()."
        )


class InstantiationError(ArchToolError):
    """A concrete implementation could not be instantiated with no arguments.

    archtool calls ``impl_class()`` during Pass 1. If the constructor requires
    arguments, pre-register the instance via ``injector.register()`` before
    calling ``inject()``.
    """

    def __init__(self, cls_name: str, original: Exception) -> None:
        super().__init__(
            f"Cannot instantiate '{cls_name}': {original}\n\n"
            f"archtool requires a no-argument __init__. "
            f"Use injector.register(InterfaceABC, your_instance) before inject() "
            f"to provide instances that need constructor arguments."
        )
