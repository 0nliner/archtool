"""Root conftest: force local archtool to load before any installed version."""

import sys
from pathlib import Path

_REPO_ROOT = str(Path(__file__).parent.resolve())

if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

# Verify archtool is importable from our version
try:
    import archtool
    _at_file = archtool.__file__
except Exception as e:
    _at_file = f"IMPORT ERROR: {e}"
