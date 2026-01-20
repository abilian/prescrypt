"""Data models for the test manager.

This module contains the core data classes used throughout the testing system:
- Status: Constants for test status values
- Program: Represents a test program
- TestResult: Result of running a single test
- Config: Configuration loaded from test-config.toml
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

# Try to import tomllib (Python 3.11+) or fall back to tomli
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None  # type: ignore[assignment]

if TYPE_CHECKING:
    from types import ModuleType

    tomllib: ModuleType | None


class Status:
    """Status constants for test results."""

    # Discovery statuses
    DISCOVERED = "DISCOVERED"

    # CPython validation statuses
    CPYTHON_PASS = "CPYTHON_PASS"  # noqa: S105
    CPYTHON_FAIL = "CPYTHON_FAIL"
    CPYTHON_SKIP = "CPYTHON_SKIP"
    CPYTHON_TIMEOUT = "CPYTHON_TIMEOUT"

    # Compilation statuses
    COMPILE_PASS = "COMPILE_PASS"  # noqa: S105
    COMPILE_FAIL = "COMPILE_FAIL"
    COMPILE_ERROR = "COMPILE_ERROR"
    COMPILE_TIMEOUT = "COMPILE_TIMEOUT"

    # Runtime statuses
    RUNTIME_PASS = "RUNTIME_PASS"  # noqa: S105
    RUNTIME_FAIL = "RUNTIME_FAIL"
    RUNTIME_ERROR = "RUNTIME_ERROR"
    RUNTIME_TIMEOUT = "RUNTIME_TIMEOUT"

    # Manual override
    MANUAL_SKIP = "MANUAL_SKIP"


@dataclass
class Program:
    """Represents a test program."""

    id: int | None
    path: str  # Relative path from programs/
    source: str  # e.g., "micropython", "tryalgo"
    first_seen_run: int | None
    last_seen_run: int | None
    cpython_status: str | None
    cpython_output: str | None
    cpython_error: str | None
    manual_skip: bool
    skip_reason: str | None

    # Note: full_path property requires PROGRAMS_DIR to be set
    # This is done by the module that uses Program
    _programs_dir: Path | None = None

    @property
    def full_path(self) -> Path:
        if self._programs_dir is None:
            from .paths import PROGRAMS_DIR

            return PROGRAMS_DIR / self.path
        return self._programs_dir / self.path

    @property
    def name(self) -> str:
        return Path(self.path).name


@dataclass
class TestResult:
    """Result of running a single test."""

    program_path: str
    status: str
    compile_time_ms: int | None = None
    runtime_ms: int | None = None
    js_output: str | None = None
    error_message: str | None = None
    error_type: str | None = None
    runtime: str | None = None  # "quickjs" or "node"


def _default_runtimes() -> list[str]:
    return ["quickjs", "node"]


def _default_include() -> list[str]:
    return ["**/*.py"]


def _default_exclude() -> list[str]:
    return ["**/__pycache__/**", "**/_*.py"]


@dataclass
class Config:
    """Configuration loaded from test-config.toml."""

    timeout: int = 10
    runtimes: list[str] = field(default_factory=_default_runtimes)
    python: str = "python3"
    programs_dir: str = "programs"
    include_patterns: list[str] = field(default_factory=_default_include)
    exclude_patterns: list[str] = field(default_factory=_default_exclude)
    micropython_only: list[str] = field(default_factory=list)
    unsupported_features: list[str] = field(default_factory=list)
    manual_skip: list[str] = field(default_factory=list)
    force_include: list[str] = field(default_factory=list)
    known_failures: list[str] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path | None = None) -> Config:
        """Load configuration from TOML file."""
        if path is None:
            from .paths import TEST_CONFIG_PATH

            path = TEST_CONFIG_PATH

        if not path.exists():
            return cls()

        if tomllib is None:
            print("Warning: tomllib/tomli not available, using defaults")
            return cls()

        with open(path, "rb") as f:
            data = tomllib.load(f)

        return cls(
            timeout=data.get("general", {}).get("timeout", 10),
            runtimes=data.get("general", {}).get("runtimes", ["quickjs", "node"]),
            python=data.get("general", {}).get("python", "python3"),
            programs_dir=data.get("discovery", {}).get("programs_dir", "programs"),
            include_patterns=data.get("discovery", {}).get("include", ["**/*.py"]),
            exclude_patterns=data.get("discovery", {}).get(
                "exclude", ["**/__pycache__/**", "**/_*.py"]
            ),
            micropython_only=data.get("classification", {}).get("micropython_only", []),
            unsupported_features=data.get("classification", {}).get(
                "unsupported_features", []
            ),
            manual_skip=data.get("manual_overrides", {}).get("skip", []),
            force_include=data.get("manual_overrides", {}).get("force_include", []),
            known_failures=data.get("manual_overrides", {}).get("known_failures", []),
        )
