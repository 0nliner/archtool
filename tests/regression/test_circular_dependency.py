"""Regression: circular dependencies produce a warning, not an error."""

from __future__ import annotations

import logging

import archtool.dependency_injector as di_module
from archtool.dependency_injector import DependencyInjector
from archtool.global_types import Dependency


class _FakeA:
    pass


class _FakeB:
    pass


def _make_cyclic_injector():
    injector = DependencyInjector(modules_list=[], layers=[])
    a_instance = _FakeA()
    b_instance = _FakeB()
    injector.dependencies["key.A"] = a_instance
    injector.dependencies["key.B"] = b_instance
    return injector, a_instance, b_instance


def test_circular_dependency_does_not_raise(caplog):
    """Cycles are valid in two-pass DI — all objects exist before setattr."""
    injector, a_instance, b_instance = _make_cyclic_injector()

    original = di_module.get_dependencies

    def _patched(container):
        if container is a_instance:
            return [Dependency(name="dep", asked="key.B")]
        if container is b_instance:
            return [Dependency(name="dep", asked="key.A")]
        return []

    di_module.get_dependencies = _patched
    try:
        with caplog.at_level(logging.WARNING, logger="archtool"):
            order = injector._topological_order()
        # must return all keys — no nodes dropped
        assert set(order) == {"key.A", "key.B"}
    finally:
        di_module.get_dependencies = original


def test_circular_dependency_emits_warning(caplog):
    """A cycle must produce exactly one WARNING so the user is aware."""
    injector, a_instance, b_instance = _make_cyclic_injector()

    original = di_module.get_dependencies

    def _patched(container):
        if container is a_instance:
            return [Dependency(name="dep", asked="key.B")]
        if container is b_instance:
            return [Dependency(name="dep", asked="key.A")]
        return []

    di_module.get_dependencies = _patched
    try:
        with caplog.at_level(logging.WARNING, logger="archtool"):
            injector._topological_order()
        warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
        assert len(warnings) == 1
        assert "Circular dependency" in warnings[0].message
    finally:
        di_module.get_dependencies = original
