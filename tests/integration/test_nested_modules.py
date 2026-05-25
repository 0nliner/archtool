"""Integration tests: nested AppModule (subpackage bounded context)."""

from __future__ import annotations

import sys
from pathlib import Path

NESTED_ROOT = Path(__file__).parent.parent / "fixtures" / "nested"


class TestNestedModuleInjection:
    def test_inject_runs_for_nested_module(self, nested_injector):
        nested_injector.inject()
        assert len(nested_injector.dependencies) > 0

    def test_service_from_nested_subpackage_registered(self, nested_injector):
        from app.core.gateway.interfaces import GatewayServiceABC

        sys.path.insert(0, str(NESTED_ROOT))
        nested_injector.inject()
        svc = nested_injector.get_dependency(GatewayServiceABC)
        assert svc is not None

    def test_repo_injected_into_nested_service(self, nested_injector):
        from app.core.gateway.interfaces import GatewayServiceABC, GatewayRepoABC

        sys.path.insert(0, str(NESTED_ROOT))
        nested_injector.inject()
        svc = nested_injector.get_dependency(GatewayServiceABC)
        assert hasattr(svc, "repo")
        assert isinstance(svc.repo, GatewayRepoABC)

    def test_service_method_works(self, nested_injector):
        from app.core.gateway.interfaces import GatewayServiceABC

        sys.path.insert(0, str(NESTED_ROOT))
        nested_injector.inject()
        svc = nested_injector.get_dependency(GatewayServiceABC)
        assert svc.check() is True
