"""Test program discovery and validation.

This module provides functions to discover test programs in the programs/
directory and validate them against CPython.
"""

from __future__ import annotations

import subprocess
from collections.abc import Iterator
from pathlib import Path

from .models import Config, Status
from .paths import PROJECT_ROOT


def discover_programs(config: Config) -> Iterator[tuple[str, str]]:
    """Discover all test programs.

    Yields (relative_path, source) tuples.
    """
    programs_dir = PROJECT_ROOT / config.programs_dir

    if not programs_dir.exists():
        print(f"Warning: Programs directory {programs_dir} does not exist")
        return

    for pattern in config.include_patterns:
        for path in programs_dir.glob(pattern):
            if not path.is_file():
                continue

            # Check exclude patterns
            rel_path = path.relative_to(programs_dir)
            rel_path_str = str(rel_path)

            excluded = False
            for exclude in config.exclude_patterns:
                if path.match(exclude):
                    excluded = True
                    break

            if excluded:
                continue

            # Determine source from first directory component
            parts = rel_path.parts
            source = parts[0] if len(parts) > 1 else "root"

            yield rel_path_str, source


def validate_cpython(
    program_path: Path, config: Config, timeout: int | None = None
) -> tuple[str, str | None, str | None]:
    """Validate that a program runs on CPython.

    Returns (status, output, error).
    """
    timeout = timeout or config.timeout

    try:
        result = subprocess.run(
            [config.python, str(program_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=program_path.parent,
            check=False,
        )

        if result.returncode == 0:
            return Status.CPYTHON_PASS, result.stdout, None
        else:
            # Check for specific skip conditions
            stderr = result.stderr
            if "ModuleNotFoundError" in stderr or "ImportError" in stderr:
                return Status.CPYTHON_SKIP, None, stderr
            if "micropython" in stderr.lower():
                return Status.CPYTHON_SKIP, None, stderr
            return Status.CPYTHON_FAIL, result.stdout, stderr

    except subprocess.TimeoutExpired:
        return Status.CPYTHON_TIMEOUT, None, f"Timeout after {timeout}s"
    except Exception as e:
        return Status.CPYTHON_FAIL, None, str(e)
