"""Shared pytest fixtures."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Fixture roots — each is a self-contained mini-project
SIMPLE_ROOT = Path(__file__).parent / "fixtures" / "simple"
NESTED_ROOT = Path(__file__).parent / "fixtures" / "nested"
FUTURE_ANN_ROOT = Path(__file__).parent / "fixtures" / "future_ann"
LAYER_VIOLATION_ROOT = Path(__file__).parent / "fixtures" / "layer_violation"


def _add_to_path(root: Path) -> None:
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_FIXTURE_ROOTS = [SIMPLE_ROOT, NESTED_ROOT, FUTURE_ANN_ROOT, LAYER_VIOLATION_ROOT]


@pytest.fixture(autouse=True)
def reset_project_root():
    """Reset archtool global project root and fixture modules after each test."""
    from archtool import utils
    original_root = utils._project_root
    original_path = sys.path[:]
    original_modules = set(sys.modules.keys())
    yield
    utils._project_root = original_root
    # Restore sys.path to pre-test state
    sys.path[:] = original_path
    # Remove fixture-related modules that were imported during the test
    for key in list(sys.modules.keys()):
        if key not in original_modules:
            sys.modules.pop(key, None)


@pytest.fixture
def simple_injector():
    """DependencyInjector wired against the 'simple' fixture project."""
    from archtool.dependency_injector import DependencyInjector
    from archtool.global_types import AppModule

    _add_to_path(SIMPLE_ROOT)
    return DependencyInjector(
        modules_list=[AppModule("app.users")],
        project_root=SIMPLE_ROOT,
    )


@pytest.fixture
def nested_injector():
    """DependencyInjector wired against the 'nested' fixture (subpackage)."""
    from archtool.dependency_injector import DependencyInjector
    from archtool.global_types import AppModule

    _add_to_path(NESTED_ROOT)
    return DependencyInjector(
        modules_list=[AppModule("app.core.gateway")],
        project_root=NESTED_ROOT,
    )


@pytest.fixture
def layer_violation_injector():
    """DependencyInjector against the fixture that has an upward layer dependency."""
    from archtool.dependency_injector import DependencyInjector
    from archtool.global_types import AppModule

    _add_to_path(LAYER_VIOLATION_ROOT)
    return DependencyInjector(
        modules_list=[AppModule("app.fraud")],
        project_root=LAYER_VIOLATION_ROOT,
    )


@pytest.fixture
def future_ann_injector():
    """DependencyInjector wired against the fixture that uses __future__ annotations."""
    from archtool.dependency_injector import DependencyInjector
    from archtool.global_types import AppModule

    _add_to_path(FUTURE_ANN_ROOT)
    return DependencyInjector(
        modules_list=[AppModule("app.billing")],
        project_root=FUTURE_ANN_ROOT,
    )
