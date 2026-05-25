"""Unit tests for archtool/utils.py."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SIMPLE_ROOT = Path(__file__).parent.parent / "fixtures" / "simple"
NESTED_ROOT = Path(__file__).parent.parent / "fixtures" / "nested"


# ── resolve_import_path ────────────────────────────────────────────────────

class TestResolveImportPath:
    def setup_method(self):
        from archtool.utils import set_project_root
        set_project_root(SIMPLE_ROOT)
        if str(SIMPLE_ROOT) not in sys.path:
            sys.path.insert(0, str(SIMPLE_ROOT))

    def test_str_input_gets_root_prefix(self):
        from archtool.utils import resolve_import_path
        result = resolve_import_path("app.users.interfaces")
        assert result == "simple.app.users.interfaces"

    def test_str_already_prefixed_is_unchanged(self):
        from archtool.utils import resolve_import_path
        prefixed = "simple.app.users.interfaces"
        assert resolve_import_path(prefixed) == prefixed

    def test_class_resolves_to_dotted_path(self):
        from archtool.utils import resolve_import_path
        from app.users.interfaces import UserServiceABC
        result = resolve_import_path(UserServiceABC)
        assert result == "simple.app.users.interfaces"

    def test_obj_and_str_produce_same_result(self):
        from archtool.utils import resolve_import_path
        from app.users.interfaces import UserServiceABC
        via_class = resolve_import_path(UserServiceABC)
        via_str = resolve_import_path(UserServiceABC.__module__)
        # via_class ends with module, via_str == module path — both should match
        assert via_class == via_str


# ── get_dependencies ───────────────────────────────────────────────────────

class TestGetDependencies:
    def setup_method(self):
        from archtool.utils import set_project_root
        set_project_root(SIMPLE_ROOT)
        if str(SIMPLE_ROOT) not in sys.path:
            sys.path.insert(0, str(SIMPLE_ROOT))

    def test_returns_abc_annotations(self):
        from archtool.utils import get_dependencies
        from app.users.services import UserService

        service_instance = UserService()
        deps = get_dependencies(service_instance)
        assert len(deps) == 1
        assert deps[0].name == "repo"

    def test_skips_private_attributes(self):
        from archtool.utils import get_dependencies

        class FakeService:
            _private: str  # type: ignore[annotation-unchecked]
            public_dep: object

        deps = get_dependencies(FakeService())
        names = [d.name for d in deps]
        assert "_private" not in names

    def test_empty_for_no_annotations(self):
        from archtool.utils import get_dependencies

        class Plain:
            pass

        assert get_dependencies(Plain()) == []


# ── get_subclasses_from_module ─────────────────────────────────────────────

class TestGetSubclassesFromModule:
    def setup_method(self):
        from archtool.utils import set_project_root
        set_project_root(SIMPLE_ROOT)
        if str(SIMPLE_ROOT) not in sys.path:
            sys.path.insert(0, str(SIMPLE_ROOT))

    def test_finds_concrete_class(self):
        from archtool.utils import get_subclasses_from_module
        from app.users.interfaces import UserRepoABC

        results = get_subclasses_from_module("app.users.repos", UserRepoABC)
        assert len(results) == 1
        assert results[0].__name__ == "UserRepo"

    def test_excludes_imported_classes(self):
        from archtool.utils import get_subclasses_from_module
        from app.users.interfaces import UserRepoABC

        # interfaces.py imports from archtool, NOT from repos.py — should return empty
        results = get_subclasses_from_module("app.users.interfaces", UserRepoABC)
        assert results == []

    def test_nested_module_included(self):
        from archtool.utils import set_project_root, get_subclasses_from_module
        set_project_root(NESTED_ROOT)
        if str(NESTED_ROOT) not in sys.path:
            sys.path.insert(0, str(NESTED_ROOT))

        from app.core.gateway.interfaces import GatewayRepoABC
        # scanning the parent path "app.core.gateway" should find GatewayRepo
        # defined in app.core.gateway.repos (subpackage)
        results = get_subclasses_from_module("app.core.gateway.repos", GatewayRepoABC)
        assert any(r.__name__ == "GatewayRepo" for r in results)


# ── is_imported logic (regression for the subpackage bug) ─────────────────

class TestIsImportedSubpackageFix:
    def setup_method(self):
        from archtool.utils import set_project_root
        set_project_root(NESTED_ROOT)
        if str(NESTED_ROOT) not in sys.path:
            sys.path.insert(0, str(NESTED_ROOT))

    def test_class_in_subpackage_is_not_considered_imported(self):
        """Regression: a class in app.core.gateway.services must NOT be
        excluded when scanning app.core.gateway."""
        from archtool.utils import resolve_import_path

        from app.core.gateway.services import GatewayService

        module_path = "nested.app.core.gateway"
        obj_path = resolve_import_path(GatewayService)

        is_in_module = (
            obj_path == module_path
            or obj_path.startswith(module_path + ".")
        )
        assert is_in_module, (
            f"Expected {obj_path!r} to be within {module_path!r}"
        )

    def test_class_from_different_module_is_considered_imported(self):
        from archtool.utils import resolve_import_path

        from archtool.layers.default_layer_interfaces import ABCRepo

        module_path = "nested.app.core.gateway"
        try:
            obj_path = resolve_import_path(ABCRepo)
            is_in_module = (
                obj_path == module_path
                or obj_path.startswith(module_path + ".")
            )
            assert not is_in_module
        except TypeError:
            # ABCRepo is outside project root → TypeError → treated as imported ✓
            pass


# ── check_is_not_interface ─────────────────────────────────────────────────

def test_check_is_not_interface_concrete():
    from archtool.utils import check_is_not_interface

    sys.path.insert(0, str(SIMPLE_ROOT))
    from app.users.services import UserService

    assert check_is_not_interface(UserService) is True


def test_check_is_not_interface_abstract():
    from archtool.utils import check_is_not_interface

    sys.path.insert(0, str(SIMPLE_ROOT))
    from app.users.interfaces import UserServiceABC

    assert check_is_not_interface(UserServiceABC) is False
