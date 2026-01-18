#!/usr/bin/env python3
"""
Script to analyze MicroPython test programs and generate a DENY_LIST.

This script:
1. Takes all programs in tests/c_e2e/from_micropython/programs/
2. Tries to compile them under CPython (checks for syntax errors)
3. Tries to run them under CPython (checks for runtime errors)
4. Reports results and outputs a DENY_LIST for test_all.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROGRAMS_DIR = Path(__file__).parent / "programs"
TIMEOUT = 5  # seconds


def check_syntax(file_path: Path) -> tuple[bool, str]:
    """Check if a file has valid Python syntax.

    Returns:
        (success, error_message)
    """
    try:
        source = file_path.read_text()
        compile(source, str(file_path), "exec")
        return True, ""
    except SyntaxError as e:
        return False, f"SyntaxError: {e.msg} (line {e.lineno})"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def run_program(file_path: Path) -> tuple[bool, str]:
    """Run a Python program and check if it exits successfully.

    Returns:
        (success, error_message)
    """
    try:
        result = subprocess.run(
            [sys.executable, str(file_path)],
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
        )
        if result.returncode == 0:
            return True, ""
        else:
            # Get the last line of stderr for a concise error
            stderr_lines = result.stderr.strip().split("\n")
            error_line = stderr_lines[-1] if stderr_lines else "Unknown error"
            return False, error_line
    except subprocess.TimeoutExpired:
        return False, "TimeoutExpired: Program hung or took too long"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def main():
    # Collect all .py files
    program_files = sorted(
        f for f in PROGRAMS_DIR.iterdir()
        if f.is_file() and f.suffix == ".py"
    )

    syntax_errors: list[tuple[str, str]] = []
    runtime_errors: list[tuple[str, str]] = []
    timeout_errors: list[tuple[str, str]] = []
    successful: list[str] = []

    print(f"Analyzing {len(program_files)} programs...\n")

    for file_path in program_files:
        filename = file_path.name

        # First check syntax
        syntax_ok, syntax_error = check_syntax(file_path)
        if not syntax_ok:
            syntax_errors.append((filename, syntax_error))
            print(f"  SYNTAX ERROR: {filename}")
            continue

        # Then try to run
        run_ok, run_error = run_program(file_path)
        if not run_ok:
            if "TimeoutExpired" in run_error:
                timeout_errors.append((filename, run_error))
                print(f"  TIMEOUT: {filename}")
            else:
                runtime_errors.append((filename, run_error))
                print(f"  RUNTIME ERROR: {filename}")
        else:
            successful.append(filename)
            print(f"  OK: {filename}")

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(f"\nTotal programs: {len(program_files)}")
    print(f"  Successful: {len(successful)}")
    print(f"  Syntax errors: {len(syntax_errors)}")
    print(f"  Runtime errors: {len(runtime_errors)}")
    print(f"  Timeouts: {len(timeout_errors)}")

    # Print detailed errors
    if syntax_errors:
        print("\n" + "-" * 70)
        print("SYNTAX ERRORS (won't compile under CPython):")
        print("-" * 70)
        for filename, error in syntax_errors:
            print(f"  {filename}")
            print(f"    {error}")

    if runtime_errors:
        print("\n" + "-" * 70)
        print("RUNTIME ERRORS (compile but fail when executed):")
        print("-" * 70)
        for filename, error in runtime_errors:
            print(f"  {filename}")
            print(f"    {error}")

    if timeout_errors:
        print("\n" + "-" * 70)
        print("TIMEOUTS (hang or take too long):")
        print("-" * 70)
        for filename, error in timeout_errors:
            print(f"  {filename}")

    # Generate DENY_LIST
    print("\n" + "=" * 70)
    print("GENERATED DENY_LIST")
    print("=" * 70)
    print("\nDENY_LIST = {")

    if timeout_errors:
        print("    # Hangs or times out")
        for filename, _ in sorted(timeout_errors):
            print(f'    "{filename}",')

    if syntax_errors:
        print("    # Syntax errors (MicroPython-specific syntax)")
        for filename, error in sorted(syntax_errors):
            # Truncate long error messages
            short_error = error[:50] + "..." if len(error) > 50 else error
            print(f'    "{filename}",  # {short_error}')

    if runtime_errors:
        print("    # Runtime errors under CPython")
        for filename, error in sorted(runtime_errors):
            # Truncate long error messages
            short_error = error[:50] + "..." if len(error) > 50 else error
            print(f'    "{filename}",  # {short_error}')

    print("}")

    # Also output just the filenames for easy copy-paste
    all_failures = (
        [f for f, _ in timeout_errors] +
        [f for f, _ in syntax_errors] +
        [f for f, _ in runtime_errors]
    )

    if all_failures:
        print("\n" + "-" * 70)
        print("PLAIN LIST (for easy copy-paste):")
        print("-" * 70)
        for filename in sorted(all_failures):
            print(f'    "{filename}",')


if __name__ == "__main__":
    main()
