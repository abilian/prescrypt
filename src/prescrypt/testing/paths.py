"""Project paths for the testing system.

These paths are used throughout the testing modules to locate project files,
the test programs directory, and the database.
"""

from __future__ import annotations

from pathlib import Path


def _find_project_root() -> Path:
    """Find the project root by looking for pyproject.toml."""
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    # Fallback: assume we're in src/prescrypt/testing/
    return Path(__file__).parent.parent.parent.parent


PROJECT_ROOT = _find_project_root()
PROGRAMS_DIR = PROJECT_ROOT / "programs"
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_PATH = DATA_DIR / "test-results.db"
TEST_CONFIG_PATH = PROJECT_ROOT / "test-config.toml"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
