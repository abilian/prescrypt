"""Unified end-to-end tests for all programs in programs/ directory.

This module replaces the separate test modules in:
- tests/c_e2e/from_micropython/test_all.py
- tests/c_e2e/whole_programs/test_all.py

It uses the test_manager database to determine which programs are eligible
for testing (those that pass CPython validation and are not manually skipped).
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

import pytest

from prescrypt.compiler import py2js
from prescrypt.testing import (
    Config,
    Program,
    PROGRAMS_DIR,
    ResultsDatabase,
    Status,
)


def get_eligible_programs() -> list[tuple[str, Program]]:
    """Get programs that are eligible for pytest execution.

    Returns programs that:
    - Pass CPython validation (CPYTHON_PASS)
    - Are not manually skipped
    """
    config = Config.load()
    db = ResultsDatabase()

    try:
        programs = db.get_programs_by_status(
            [Status.CPYTHON_PASS], exclude_manual_skip=True
        )
        # Return (test_id, program) tuples for parametrization
        return [(p.path, p) for p in programs]
    finally:
        db.close()


def get_known_failures() -> set[str]:
    """Get set of known failure paths from config."""
    config = Config.load()
    return set(config.known_failures)


# Cache the eligible programs at module load time
_ELIGIBLE_PROGRAMS = None
_KNOWN_FAILURES = None


def _get_cached_programs():
    global _ELIGIBLE_PROGRAMS
    if _ELIGIBLE_PROGRAMS is None:
        _ELIGIBLE_PROGRAMS = get_eligible_programs()
    return _ELIGIBLE_PROGRAMS


def _get_cached_known_failures():
    global _KNOWN_FAILURES
    if _KNOWN_FAILURES is None:
        _KNOWN_FAILURES = get_known_failures()
    return _KNOWN_FAILURES


@pytest.fixture
def known_failures():
    return _get_cached_known_failures()


def pytest_generate_tests(metafunc):
    """Generate test parameters from eligible programs."""
    if "program_path" in metafunc.fixturenames:
        programs = _get_cached_programs()
        if programs:
            ids = [p[0] for p in programs]
            metafunc.parametrize(
                "program_path,program",
                programs,
                ids=ids,
            )
        else:
            # No programs found - skip all tests
            metafunc.parametrize("program_path,program", [])


def test_program(program_path: str, program: Program, known_failures: set[str]):
    """Test a single program through the Prescrypt pipeline.

    1. Compile Python to JavaScript
    2. Run JavaScript with Node.js
    3. Compare output with stored CPython output
    """
    src_path = PROGRAMS_DIR / program_path

    if not src_path.exists():
        pytest.skip(f"Program file not found: {src_path}")

    # Check if this is a known failure
    if program_path in known_failures:
        pytest.xfail(f"Known failure: {program_path}")

    # Read source and compile to JavaScript
    source = src_path.read_text()
    try:
        js_code = py2js(source)
    except Exception as e:
        pytest.fail(f"Compilation failed: {e}")

    # Write JS to temp file and execute with Node.js
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".js", delete=False
    ) as tmp:
        tmp.write(js_code)
        tmp_path = Path(tmp.name)

    try:
        result = subprocess.run(
            ["node", str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )

        js_output = result.stdout.strip()
        js_stderr = result.stderr.strip()

        # Get expected output from database (CPython output)
        expected_output = (program.cpython_output or "").strip()

        # Check for runtime errors
        if result.returncode != 0:
            # Show useful debug info
            print(f"\n\nJavaScript execution failed (exit code {result.returncode})")
            print(f"stderr: {js_stderr}")
            print(f"\nGenerated JS (without stdlib):")
            print(py2js(source, include_stdlib=False))
            pytest.fail(f"JavaScript runtime error: {js_stderr}")

        # Compare outputs
        if js_output != expected_output:
            print(f"\n\nOutput mismatch for {program_path}")
            print(f"Expected (Python):\n{expected_output}")
            print(f"\nActual (JavaScript):\n{js_output}")
            print(f"\nGenerated JS (without stdlib):")
            print(py2js(source, include_stdlib=False))
            pytest.fail(
                f"Output mismatch: expected {expected_output!r}, got {js_output!r}"
            )

    except subprocess.TimeoutExpired:
        pytest.fail("JavaScript execution timed out (>10s)")

    finally:
        tmp_path.unlink(missing_ok=True)
