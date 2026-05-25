"""Regression: DI must work when components use 'from __future__ import annotations'."""

from __future__ import annotations

import sys
from pathlib import Path

FUTURE_ANN_ROOT = Path(__file__).parent.parent / "fixtures" / "future_ann"


class TestFutureAnnotations:
    """All annotations in the billing fixture are strings at runtime.
    archtool must still resolve and inject them correctly.
    """

    def test_inject_runs_without_error(self, future_ann_injector):
        future_ann_injector.inject()

    def test_service_registered(self, future_ann_injector):
        from app.billing.interfaces import BillingServiceABC

        sys.path.insert(0, str(FUTURE_ANN_ROOT))
        future_ann_injector.inject()
        svc = future_ann_injector.get_dependency(BillingServiceABC)
        assert svc is not None

    def test_repo_injected_despite_string_annotation(self, future_ann_injector):
        """Core regression: repo must be injected even when the annotation
        'repo: BillingRepoABC' is stored as a string by __future__."""
        from app.billing.interfaces import BillingServiceABC, BillingRepoABC

        sys.path.insert(0, str(FUTURE_ANN_ROOT))
        future_ann_injector.inject()
        svc = future_ann_injector.get_dependency(BillingServiceABC)

        assert hasattr(svc, "repo"), (
            "DI failed to inject 'repo' — likely a __future__ annotations regression"
        )
        assert isinstance(svc.repo, BillingRepoABC)

    def test_service_method_works_after_injection(self, future_ann_injector):
        from app.billing.interfaces import BillingServiceABC

        sys.path.insert(0, str(FUTURE_ANN_ROOT))
        future_ann_injector.inject()
        svc = future_ann_injector.get_dependency(BillingServiceABC)
        total = svc.total()
        assert isinstance(total, float)
        assert total == 100.0
