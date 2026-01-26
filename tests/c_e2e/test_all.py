"""End-to-end tests for programs in the programs/ directory.

Discovers test programs from the filesystem using patterns from test-config.toml.
No database dependency - runs Python at test time to get expected output.

Tests are split into two categories:
- internal: Core language feature tests (programs/internal/*.py)
- tryalgo: Algorithm tests (programs/tryalgo/test_*.py)
"""

from __future__ import annotations

import re
import subprocess
import tempfile
from functools import cache
from pathlib import Path

import pytest

from prescrypt.compiler import py2js
from prescrypt.testing import PROJECT_ROOT, Config


@cache
def get_config() -> Config:
    """Load and cache the test configuration."""
    return Config.load()


@cache
def get_programs_dir() -> Path:
    """Get the programs directory from config."""
    config = get_config()
    return PROJECT_ROOT / config.programs_dir


def _glob_to_regex(pattern: str) -> str:
    """Convert a glob pattern to a regex pattern."""
    # Escape special regex chars except * and ?
    pattern = re.escape(pattern)
    # Convert **/ to match zero or more directories
    pattern = pattern.replace(r"\*\*/", "(.*/)?")
    # Convert remaining ** to match anything
    pattern = pattern.replace(r"\*\*", ".*")
    # Convert * to match any non-/ chars
    pattern = pattern.replace(r"\*", "[^/]*")
    # Convert ? to match single char
    pattern = pattern.replace(r"\?", ".")
    return "^" + pattern + "$"


def _matches_patterns(path: str, patterns: list[str]) -> bool:
    """Check if path matches any of the glob patterns."""
    for pattern in patterns:
        regex = _glob_to_regex(pattern)
        if re.match(regex, path):
            return True
    return False


@cache
def discover_programs(category: str | None = None) -> list[str]:
    """Discover test programs from filesystem using config patterns.

    Args:
        category: Filter by category ("internal", "tryalgo", or None for all)

    Returns list of paths relative to programs_dir.
    """
    config = get_config()
    programs_dir = get_programs_dir()

    if not programs_dir.exists():
        return []

    programs = []

    # Find all .py files in programs_dir
    for py_file in programs_dir.rglob("*.py"):
        # Get path relative to programs_dir
        rel_path = str(py_file.relative_to(programs_dir))

        # Must match at least one include pattern
        if not _matches_patterns(rel_path, config.include_patterns):
            continue

        # Must not match any exclude pattern
        if _matches_patterns(rel_path, config.exclude_patterns):
            continue

        # Filter by category if specified
        if category == "internal" and not rel_path.startswith("internal/"):
            continue
        if category == "tryalgo" and not rel_path.startswith("tryalgo/"):
            continue

        programs.append(rel_path)

    return sorted(programs)


@cache
def get_known_failures() -> set[str]:
    """Get set of known failure paths from config."""
    config = get_config()
    return set(config.known_failures)


def run_python(file_path: Path, timeout: int = 10) -> tuple[str, int]:
    """Run a Python file and return (output, return_code)."""
    config = get_config()
    try:
        result = subprocess.run(
            [config.python, str(file_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=file_path.parent,
        )
        return result.stdout.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", -1


@pytest.fixture
def known_failures():
    return get_known_failures()


def pytest_generate_tests(metafunc):
    """Generate test parameters from discovered programs."""
    if "internal_program" in metafunc.fixturenames:
        programs = discover_programs("internal")
        if programs:
            metafunc.parametrize("internal_program", programs, ids=programs)
        else:
            metafunc.parametrize("internal_program", [])
    elif "tryalgo_program" in metafunc.fixturenames:
        programs = discover_programs("tryalgo")
        if programs:
            metafunc.parametrize("tryalgo_program", programs, ids=programs)
        else:
            metafunc.parametrize("tryalgo_program", [])
    elif "program_path" in metafunc.fixturenames:
        # Legacy: all programs
        programs = discover_programs()
        if programs:
            metafunc.parametrize("program_path", programs, ids=programs)
        else:
            metafunc.parametrize("program_path", [])


def _run_program_test(program_path: str, known_failures: set[str]):
    """Test a single program through the Prescrypt pipeline.

    1. Run Python to get expected output
    2. Compile Python to JavaScript
    3. Run JavaScript with Node.js
    4. Compare outputs
    """
    src_path = get_programs_dir() / program_path

    if not src_path.exists():
        pytest.skip(f"Program file not found: {src_path}")

    # Check if this is a known failure
    if program_path in known_failures:
        pytest.xfail(f"Known failure: {program_path}")

    # Run Python to get expected output
    expected_output, py_returncode = run_python(src_path)
    if py_returncode != 0:
        pytest.skip(f"Python execution failed (exit code {py_returncode})")

    # Read source and compile to JavaScript
    source = src_path.read_text()
    try:
        js_code = py2js(source)
    except Exception as e:
        pytest.fail(f"Compilation failed: {e}")

    # Write JS to temp file and execute with Node.js
    with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as tmp:
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

        # Check for runtime errors
        if result.returncode != 0:
            print(f"\n\nJavaScript execution failed (exit code {result.returncode})")
            print(f"stderr: {js_stderr}")
            # print("\nGenerated JS (without stdlib):")
            # print(py2js(source, include_stdlib=False))
            pytest.fail(f"JavaScript runtime error: {js_stderr}")

        # Compare outputs
        if js_output != expected_output:
            print(f"\n\n# Output mismatch for {program_path}")
            print(f"## Expected (Python):\n\n```\n{expected_output}\n```\n\n")
            print(f"## Actual (JavaScript):\n\n```\n{js_output}\n```\n")
            # print("\nGenerated JS (without stdlib):")
            # print(py2js(source, include_stdlib=False))
            pytest.fail("Output mismatch")

    except subprocess.TimeoutExpired:
        pytest.fail("JavaScript execution timed out (>10s)")

    finally:
        tmp_path.unlink(missing_ok=True)


def test_internal_program(internal_program: str, known_failures: set[str]):
    """Test an internal (core language feature) program."""
    _run_program_test(internal_program, known_failures)


def test_tryalgo_program(tryalgo_program: str, known_failures: set[str]):
    """Test a tryalgo (algorithm) program."""
    _run_program_test(tryalgo_program, known_failures)


def test_program(program_path: str, known_failures: set[str]):
    """Test a single program (legacy - all programs)."""
    _run_program_test(program_path, known_failures)
