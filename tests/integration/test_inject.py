"""Integration tests: full DI cycle."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SIMPLE_ROOT = Path(__file__).parent.parent / "fixtures" / "simple"
LAYER_VIOLATION_ROOT = Path(__file__).parent.parent / "fixtures" / "layer_violation"


class TestBasicInjection:
    def test_inject_runs_without_error(self, simple_injector):
        simple_injector.inject()

    def test_service_is_registered(self, simple_injector):
        from app.users.interfaces import UserServiceABC

        sys.path.insert(0, str(SIMPLE_ROOT))
        simple_injector.inject()
        svc = simple_injector.get_dependency(UserServiceABC)
        assert svc is not None

    def test_repo_injected_into_service(self, simple_injector):
        from app.users.interfaces import UserServiceABC, UserRepoABC

        sys.path.insert(0, str(SIMPLE_ROOT))
        simple_injector.inject()
        svc = simple_injector.get_dependency(UserServiceABC)
        assert hasattr(svc, "repo")
        assert isinstance(svc.repo, UserRepoABC)

    def test_service_method_works_after_injection(self, simple_injector):
        from app.users.interfaces import UserServiceABC

        sys.path.insert(0, str(SIMPLE_ROOT))
        simple_injector.inject()
        svc = simple_injector.get_dependency(UserServiceABC)
        result = svc.get_name()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_dependency_by_class(self, simple_injector):
        from app.users.interfaces import UserRepoABC

        sys.path.insert(0, str(SIMPLE_ROOT))
        simple_injector.inject()
        repo = simple_injector.get_dependency(UserRepoABC)
        assert repo is not None

    def test_inject_is_idempotent(self, simple_injector):
        """Calling inject() twice must not raise — already-registered deps are skipped."""
        simple_injector.inject()
        count_after_first = len(simple_injector.dependencies)
        simple_injector.inject()  # should not raise DependencyDuplicate
        assert len(simple_injector.dependencies) == count_after_first

    def test_missing_dependency_raises(self, simple_injector):
        from archtool.exceptions import DependencyDoesNotRegistred
        from archtool.layers.default_layer_interfaces import ABCView  # not registered

        simple_injector.inject()
        with pytest.raises(DependencyDoesNotRegistred):
            simple_injector.get_dependency(ABCView)


class TestManualRegistration:
    """injector.register() lets users wire anything archtool can't auto-discover."""

    def test_manually_registered_dep_is_retrievable(self, simple_injector):
        from app.users.interfaces import UserRepoABC
        from app.users.repos import UserRepo

        sys.path.insert(0, str(SIMPLE_ROOT))
        instance = UserRepo()
        simple_injector.register(key=UserRepoABC, value=instance)
        retrieved = simple_injector.get_dependency(UserRepoABC)
        assert retrieved is instance

    def test_manual_dep_is_injected_into_auto_component(self, simple_injector):
        """A manually-registered repo is injected into an auto-discovered service."""
        from app.users.interfaces import UserRepoABC, UserServiceABC
        from app.users.repos import UserRepo

        sys.path.insert(0, str(SIMPLE_ROOT))

        custom_repo = UserRepo()
        simple_injector.register(key=UserRepoABC, value=custom_repo)
        simple_injector.inject()

        svc = simple_injector.get_dependency(UserServiceABC)
        assert svc.repo is custom_repo

    def test_dependencies_dict_is_publicly_accessible(self, simple_injector):
        simple_injector.inject()
        assert isinstance(simple_injector.dependencies, dict)
        assert len(simple_injector.dependencies) > 0

    def test_duplicate_manual_registration_raises(self, simple_injector):
        from archtool.exceptions import DependencyDuplicate
        from app.users.interfaces import UserRepoABC
        from app.users.repos import UserRepo

        sys.path.insert(0, str(SIMPLE_ROOT))
        simple_injector.register(key=UserRepoABC, value=UserRepo())
        with pytest.raises(DependencyDuplicate):
            simple_injector.register(key=UserRepoABC, value=UserRepo())


class TestLayerEnforcement:
    """Layer boundary violations are caught at startup, between pass 1 and pass 2."""

    def test_correct_layer_dependencies_pass(self, simple_injector):
        """service → repo (Domain → Infrastructure) is a valid downward dependency."""
        simple_injector.inject()  # must not raise

    def test_service_depending_on_controller_raises(self, layer_violation_injector):
        """service depends on controller (Domain → Application) — upward dep, must raise."""
        from archtool.exceptions import TopLevelLayerUsingException

        with pytest.raises(TopLevelLayerUsingException) as exc_info:
            layer_violation_injector.inject()

        msg = str(exc_info.value)
        assert "FraudService" in msg
        assert "DomainLayer" in msg
        assert "ApplicationLayer" in msg

    def test_violation_error_names_the_bad_dependency(self, layer_violation_injector):
        """Error message must name the offending dependency interface."""
        from archtool.exceptions import TopLevelLayerUsingException

        with pytest.raises(TopLevelLayerUsingException) as exc_info:
            layer_violation_injector.inject()

        assert "FraudControllerABC" in str(exc_info.value)

    def test_enforce_layers_false_skips_check(self, layer_violation_injector):
        """enforce_layers=False disables the check — violating project assembles without error."""
        from archtool.dependency_injector import DependencyInjector
        from archtool.global_types import AppModule

        sys.path.insert(0, str(LAYER_VIOLATION_ROOT))
        injector = DependencyInjector(
            modules_list=[AppModule("app.fraud")],
            project_root=LAYER_VIOLATION_ROOT,
            enforce_layers=False,
        )
        injector.inject()  # must not raise

    def test_manually_registered_dep_bypasses_layer_check(self, layer_violation_injector):
        """Pre-registering the controller skips its auto-discovery and layer check."""
        sys.path.insert(0, str(LAYER_VIOLATION_ROOT))
        from app.fraud.interfaces import FraudControllerABC
        from app.fraud.controllers import FraudController

        # Pre-register the controller so it's not auto-discovered.
        # _component_to_layer won't have an entry for it → check is skipped.
        layer_violation_injector.register(key=FraudControllerABC, value=FraudController())
        layer_violation_injector.inject()  # must not raise

    def test_component_to_layer_populated_after_inject(self, simple_injector):
        """_component_to_layer is populated during pass 1 for all auto-discovered components."""
        from archtool.layers.default_layers import DomainLayer, InfrastructureLayer

        sys.path.insert(0, str(SIMPLE_ROOT))
        simple_injector.inject()

        layers_found = {type(v) for v in simple_injector._component_to_layer.values()}
        assert DomainLayer in layers_found
        assert InfrastructureLayer in layers_found

    def test_same_layer_dependencies_are_allowed(self):
        """Two services in the same module can depend on each other (same-layer dep)."""
        # The simple fixture has service → repo (cross-layer, allowed).
        # This test verifies the allowed-set includes the component's own layer.
        from archtool.dependency_injector import DependencyInjector
        from archtool.layers.default_layers import DomainLayer, InfrastructureLayer

        injector = DependencyInjector.__new__(DependencyInjector)
        injector._enforce_layers = True
        injector._component_to_layer = {}

        fake_layer_a = DomainLayer()
        fake_layer_b = DomainLayer()

        allowed = injector._get_allowed_layer_types(fake_layer_a)
        # same layer type must be in the allowed set
        assert DomainLayer in allowed
        # lower layer must be transitively allowed
        assert InfrastructureLayer in allowed
        # upper layer must NOT be allowed
        from archtool.layers.default_layers import ApplicationLayer
        assert ApplicationLayer not in allowed
