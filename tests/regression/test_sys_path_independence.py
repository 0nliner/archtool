"""Regression: DI must work regardless of sys.path[0] content."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SIMPLE_ROOT = Path(__file__).parent.parent / "fixtures" / "simple"


class TestSysPathIndependence:
    """archtool v1 relied on sys.path[0] for path resolution.
    v2 uses an explicit project_root parameter.
    These tests verify that DI works even when sys.path[0] is wrong.
    """

    def test_inject_works_when_sys_path_zero_is_subdir(self, monkeypatch, simple_injector):
        """Simulate running from entrypoints/ — sys.path[0] is a subdir."""
        fake_subdir = str(SIMPLE_ROOT / "entrypoints")
        monkeypatch.syspath_prepend(fake_subdir)

        # ensure the real root is still importable
        if str(SIMPLE_ROOT) not in sys.path:
            sys.path.insert(1, str(SIMPLE_ROOT))

        # DI uses explicit project_root, so sys.path[0] doesn't matter
        simple_injector.inject()
        assert len(simple_injector.dependencies) > 0

    def test_inject_works_when_cwd_is_different(self, tmp_path, simple_injector):
        """project_root is explicit — cwd is irrelevant."""
        # Change cwd to a temp directory that has nothing to do with the project
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)
            simple_injector.inject()
            assert len(simple_injector.dependencies) > 0
        finally:
            import os
            os.chdir(original_cwd)

    def test_project_root_overrides_detection(self):
        """Explicitly passed project_root takes priority over auto-detection."""
        from archtool.utils import set_project_root, get_project_root

        set_project_root(SIMPLE_ROOT)
        assert get_project_root() == SIMPLE_ROOT.resolve()

    def test_verbose_env_var_controls_logging(self, monkeypatch):
        """ARCHTOOL_VERBOSE=1 enables debug logging without code changes."""
        import logging
        from archtool.dependency_injector import DependencyInjector
        from archtool.global_types import AppModule

        monkeypatch.setenv("ARCHTOOL_VERBOSE", "1")
        if str(SIMPLE_ROOT) not in sys.path:
            sys.path.insert(0, str(SIMPLE_ROOT))

        injector = DependencyInjector(
            modules_list=[AppModule("app.users")],
            project_root=SIMPLE_ROOT,
        )
        lib_logger = logging.getLogger("archtool")
        assert lib_logger.level == logging.DEBUG
