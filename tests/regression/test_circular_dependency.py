"""Regression: circular dependencies must be detected and reported clearly."""

from __future__ import annotations

import pytest
from archtool.dependency_injector import DependencyInjector
from archtool.exceptions import CircularDependencyError


class _FakeABC:
    pass


class _FakeA(_FakeABC):
    pass


class _FakeBBC:
    pass


class _FakeB(_FakeBBC):
    b_dep: _FakeABC  # A → B is fine, but we'll wire B → A manually to create a cycle


def test_circular_dependency_raises_on_inject():
    """Manually register two instances that depend on each other."""
    injector = DependencyInjector(modules_list=[], layers=[])

    a_instance = _FakeA()
    b_instance = _FakeB()

    # Wire the cycle by patching dependencies onto instances directly
    # so _topological_order sees a → b → a
    injector.dependencies["key.A"] = a_instance
    injector.dependencies["key.B"] = b_instance

    # Patch get_dependencies in the dependency_injector module (that's where it's imported)
    import archtool.dependency_injector as di_module
    from archtool.global_types import Dependency

    original = di_module.get_dependencies

    def _patched(container):
        if container is a_instance:
            return [Dependency(name="dep", asked="key.B")]
        if container is b_instance:
            return [Dependency(name="dep", asked="key.A")]
        return []

    di_module.get_dependencies = _patched
    try:
        with pytest.raises(CircularDependencyError) as exc_info:
            injector._topological_order()
        assert "key.A" in str(exc_info.value) or "key.B" in str(exc_info.value)
    finally:
        di_module.get_dependencies = original
