"""Unit tests for exception messages and hierarchy."""

from __future__ import annotations

import pytest
from archtool.exceptions import (
    ArchToolError,
    CircularDependencyError,
    DependencyDuplicate,
    DependencyDoesNotRegistred,
    InstantiationError,
    RealizationNotFound,
    RealizationNotFount,  # backward-compat alias
    MultipleRealizationsException,
    ModuleValidationError,
)


def test_all_exceptions_inherit_from_arch_tool_error():
    for exc_class in (
        DependencyDuplicate,
        MultipleRealizationsException,
        RealizationNotFound,
        ModuleValidationError,
    ):
        assert issubclass(exc_class, ArchToolError)


def test_dependency_duplicate_message():
    exc = DependencyDuplicate("myproject.app.users.interfaces.UserServiceABC")
    assert "UserServiceABC" in str(exc)
    assert "already registered" in str(exc)


def test_dependency_not_registered_with_hint():
    exc = DependencyDoesNotRegistred(
        "myproject.app.users.interfaces.UserServiceABC",
        registered=["myproject.app.users.interfaces.UserRepoABC"],
    )
    msg = str(exc)
    assert "UserServiceABC" in msg
    assert "UserRepoABC" in msg  # hint listing registered deps


def test_realization_not_found_message():
    exc = RealizationNotFound("No realization of 'UserServiceABC' found")
    assert "UserServiceABC" in str(exc)


def test_realization_not_fount_is_alias():
    assert RealizationNotFount is RealizationNotFound


def test_module_validation_error_lists_problems():
    exc = ModuleValidationError("app.users", ["Missing interfaces.py", "No repos.py"])
    msg = str(exc)
    assert "interfaces.py" in msg
    assert "repos.py" in msg


def test_circular_dependency_error_shows_cycle():
    cycle = [
        "myproject.app.a.interfaces.ServiceA",
        "myproject.app.b.interfaces.ServiceB",
        "myproject.app.a.interfaces.ServiceA",
    ]
    exc = CircularDependencyError(cycle)
    msg = str(exc)
    assert "ServiceA" in msg
    assert "ServiceB" in msg
    assert "→" in msg


def test_instantiation_error_mentions_class_and_hint():
    exc = InstantiationError("UserService", TypeError("__init__ requires 1 argument"))
    msg = str(exc)
    assert "UserService" in msg
    assert "injector.register" in msg
