#!/usr/bin/env python3
"""
Comprehensive diagnostic script for MicroPython test programs.

This script:
1. Takes all programs in tests/c_e2e/from_micropython/programs/
2. Compiles them with py2js (in a subprocess to handle hangs)
3. Runs the generated JavaScript with QuickJS
4. Runs the generated JavaScript with Node.js
5. Reports detailed diagnostics for any failures

Usage:
    python check_all.py [--verbose] [--filter PATTERN] [--show-js]
    python check_all.py --create-denylist   # Generate DENY_LIST for test_all.py
    python check_all.py --update-denylist   # Test denylist, show newly passing + updated list
    python check_all.py -q                  # Quiet mode: outputs "failures/total"
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import traceback
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

PROGRAMS_DIR = Path(__file__).parent / "programs"
TIMEOUT = 10  # seconds for JS execution
COMPILE_TIMEOUT = 5  # seconds for compilation


class Status(Enum):
    SUCCESS = "success"
    COMPILE_ERROR = "compile_error"
    COMPILE_TIMEOUT = "compile_timeout"
    QUICKJS_ERROR = "quickjs_error"
    NODE_ERROR = "node_error"
    QUICKJS_TIMEOUT = "quickjs_timeout"
    NODE_TIMEOUT = "node_timeout"
    OUTPUT_MISMATCH = "output_mismatch"


@dataclass
class ProgramResult:
    """Result of testing a single program."""

    filename: str
    status: Status

    # Compilation results
    compile_success: bool = False
    compile_error: str = ""
    compile_traceback: str = ""
    js_code: str = ""

    # QuickJS results
    quickjs_success: bool = False
    quickjs_stdout: str = ""
    quickjs_stderr: str = ""
    quickjs_returncode: int = -1
    quickjs_error: str = ""

    # Node.js results
    node_success: bool = False
    node_stdout: str = ""
    node_stderr: str = ""
    node_returncode: int = -1
    node_error: str = ""

    # Python reference (optional)
    python_stdout: str = ""
    python_stderr: str = ""
    python_success: bool = False

    # Output mismatch info
    output_mismatch: bool = False


# Helper script for subprocess-based compilation
_COMPILE_SCRIPT = """
import sys
import json
import traceback
from pathlib import Path

# Try to set memory limit (512 MB) to prevent OOM - only works on Linux
try:
    import resource
    MAX_MEMORY = 512 * 1024 * 1024  # 512 MB
    resource.setrlimit(resource.RLIMIT_AS, (MAX_MEMORY, MAX_MEMORY))
except Exception:
    pass  # RLIMIT_AS not supported on macOS, or other error

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))
from prescrypt.compiler import py2js

source_path = sys.argv[1]
try:
    source = Path(source_path).read_text()
    js_code = py2js(source)
    print(json.dumps({"status": "success", "js_code": js_code, "error": "", "traceback": ""}))
except MemoryError:
    print(json.dumps({"status": "error", "js_code": "", "error": "MemoryError: compilation exhausted memory limit", "traceback": ""}))
except Exception as e:
    print(json.dumps({"status": "error", "js_code": "", "error": str(e), "traceback": traceback.format_exc()}))
"""

# Memory limit for compilation subprocess (512 MB)
COMPILE_MEMORY_LIMIT = 512 * 1024 * 1024


def _set_memory_limit():
    """Set memory limit for the subprocess. Called via preexec_fn.

    Note: RLIMIT_AS doesn't work on macOS, so this is a no-op there.
    On Linux, this helps prevent OOM situations.
    """
    try:
        import resource
        # Try RLIMIT_AS (address space) - works on Linux
        resource.setrlimit(resource.RLIMIT_AS, (COMPILE_MEMORY_LIMIT, COMPILE_MEMORY_LIMIT))
    except (ValueError, OSError, AttributeError):
        # RLIMIT_AS not supported (macOS) or other error - just skip
        pass


def compile_program(
    source_path: Path, timeout: int = COMPILE_TIMEOUT
) -> tuple[str, str, str, str]:
    """Compile a Python file to JavaScript in a separate subprocess.

    Uses Popen for better control over process termination.
    Sets memory limits to prevent OOM situations.

    Returns:
        (status, js_code, error_message, traceback)
        status is one of: "success", "error", "timeout"
    """
    import os
    import signal

    # Create the helper script file
    script_path = Path(__file__).parent / "_compile_helper.py"

    try:
        # Write the helper script if it doesn't exist
        if not script_path.exists():
            script_path.write_text(_COMPILE_SCRIPT)

        # Start the compilation in a subprocess with its own process group
        process = subprocess.Popen(
            [sys.executable, str(script_path), str(source_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,  # Create new process group for clean killing
            preexec_fn=_set_memory_limit,
        )

        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            # Kill the entire process group
            try:
                os.killpg(os.getpgid(process.pid), signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                process.kill()
            process.wait()
            return (
                "timeout",
                "",
                f"Compilation timed out after {timeout} seconds (possible infinite loop or memory exhaustion)",
                "",
            )

        if process.returncode != 0:
            # Check for memory-related signals
            if process.returncode == -signal.SIGKILL:
                return "timeout", "", "Compilation killed (likely OOM or timeout)", ""
            if process.returncode == -signal.SIGSEGV:
                return "error", "", "Compilation crashed (segmentation fault)", ""
            return (
                "error",
                "",
                f"Subprocess error (exit {process.returncode}): {stderr[:500]}",
                "",
            )

        # Parse the JSON output
        try:
            data = json.loads(stdout)
            return data["status"], data["js_code"], data["error"], data["traceback"]
        except json.JSONDecodeError:
            return "error", "", f"Failed to parse compiler output: {stdout[:200]}", ""

    except Exception as e:
        return "error", "", f"Compilation failed: {e}", traceback.format_exc()


def run_quickjs(
    js_code: str, timeout: int = TIMEOUT
) -> tuple[bool, str, str, int, str]:
    """Run JavaScript code with QuickJS (qjs) as external process.

    Returns:
        (success, stdout, stderr, returncode, error_message)
    """
    import os
    import signal

    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
            f.write(js_code)
            temp_path = Path(f.name)

        try:
            # Run qjs in its own process group for clean killing
            process = subprocess.Popen(
                ["qjs", str(temp_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                start_new_session=True,
                preexec_fn=_set_memory_limit,
            )

            try:
                stdout, stderr = process.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                # Kill the entire process group
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                except (ProcessLookupError, PermissionError):
                    process.kill()
                process.wait()
                return False, "", "", -1, f"TimeoutExpired: QuickJS took longer than {timeout}s"

            success = process.returncode == 0
            error = ""
            if not success and stderr:
                # QuickJS errors: first line has the error, rest is stack trace
                # e.g., "ReferenceError: 'foo' is not defined\n    at /tmp/foo.js:42"
                lines = [l for l in stderr.strip().split("\n") if l.strip()]
                error = lines[0] if lines else f"Exit code {process.returncode}"
            elif not success:
                error = f"Exit code {process.returncode}"
            return success, stdout.strip(), stderr.strip(), process.returncode, error
        finally:
            temp_path.unlink()

    except FileNotFoundError:
        return False, "", "", -1, "qjs not found in PATH (install QuickJS)"
    except Exception as e:
        return False, "", "", -1, f"QuickJS error: {e}"


def run_node(js_code: str, timeout: int = TIMEOUT) -> tuple[bool, str, str, int, str]:
    """Run JavaScript code with Node.js as external process.

    Returns:
        (success, stdout, stderr, returncode, error_message)
    """
    import os
    import signal

    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
            f.write(js_code)
            temp_path = Path(f.name)

        try:
            # Run node in its own process group for clean killing
            process = subprocess.Popen(
                ["node", str(temp_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                start_new_session=True,
                preexec_fn=_set_memory_limit,
            )

            try:
                stdout, stderr = process.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                # Kill the entire process group
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                except (ProcessLookupError, PermissionError):
                    process.kill()
                process.wait()
                return False, "", "", -1, f"TimeoutExpired: Node.js took longer than {timeout}s"

            success = process.returncode == 0
            error = ""
            if not success and stderr:
                # Node.js errors: look for line with error type (contains "Error:")
                # e.g., "ReferenceError: foo is not defined\n    at Object.<anonymous>..."
                lines = [l for l in stderr.strip().split("\n") if l.strip()]
                # Find first line containing an error type
                for line in lines:
                    if "Error:" in line or "Error " in line:
                        error = line.strip()
                        break
                if not error:
                    error = lines[0] if lines else f"Exit code {process.returncode}"
            elif not success:
                error = f"Exit code {process.returncode}"
            return success, stdout.strip(), stderr.strip(), process.returncode, error
        finally:
            temp_path.unlink()

    except FileNotFoundError:
        return False, "", "", -1, "Node.js not found in PATH"
    except Exception as e:
        return False, "", "", -1, f"Node error: {e}"


def run_python(source_path: Path, timeout: int = TIMEOUT) -> tuple[bool, str, str]:
    """Run Python source for reference output.

    Returns:
        (success, stdout, stderr)
    """
    try:
        result = subprocess.run(
            [sys.executable, str(source_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "", "TimeoutExpired"
    except Exception as e:
        return False, "", str(e)


def test_program(
    source_path: Path,
    run_python_ref: bool = True,
    compile_timeout: int = COMPILE_TIMEOUT,
    run_timeout: int = TIMEOUT,
) -> ProgramResult:
    """Test a single program through the full pipeline."""
    result = ProgramResult(
        filename=source_path.name,
        status=Status.SUCCESS,
    )

    # Step 1: Compile (in a separate process with timeout)
    compile_status, js_code, compile_err, compile_tb = compile_program(
        source_path, compile_timeout
    )
    result.compile_success = compile_status == "success"
    result.js_code = js_code
    result.compile_error = compile_err
    result.compile_traceback = compile_tb

    if compile_status == "timeout":
        result.status = Status.COMPILE_TIMEOUT
        return result
    elif compile_status == "error":
        result.status = Status.COMPILE_ERROR
        return result

    # Step 2: Run with QuickJS
    qjs_ok, qjs_stdout, qjs_stderr, qjs_rc, qjs_err = run_quickjs(js_code, run_timeout)
    result.quickjs_success = qjs_ok
    result.quickjs_stdout = qjs_stdout
    result.quickjs_stderr = qjs_stderr
    result.quickjs_returncode = qjs_rc
    result.quickjs_error = qjs_err

    if not qjs_ok:
        if "timeout" in qjs_err.lower():
            result.status = Status.QUICKJS_TIMEOUT
        else:
            result.status = Status.QUICKJS_ERROR

    # Step 3: Run with Node.js
    node_ok, node_stdout, node_stderr, node_rc, node_err = run_node(
        js_code, run_timeout
    )
    result.node_success = node_ok
    result.node_stdout = node_stdout
    result.node_stderr = node_stderr
    result.node_returncode = node_rc
    result.node_error = node_err

    if not node_ok and result.status == Status.SUCCESS:
        if "timeout" in node_err.lower():
            result.status = Status.NODE_TIMEOUT
        else:
            result.status = Status.NODE_ERROR

    # Step 4: Get Python reference output (optional)
    if run_python_ref:
        py_ok, py_stdout, py_stderr = run_python(source_path, run_timeout)
        result.python_success = py_ok
        result.python_stdout = py_stdout
        result.python_stderr = py_stderr

        # Step 5: Check for output mismatch (only if everything ran successfully)
        if (
            result.status == Status.SUCCESS
            and result.node_success
            and py_ok
            and result.node_stdout != py_stdout
        ):
            result.output_mismatch = True
            result.status = Status.OUTPUT_MISMATCH

    return result


def format_code_block(code: str, max_lines: int = 50) -> str:
    """Format a code block, truncating if too long."""
    lines = code.split("\n")
    if len(lines) > max_lines:
        return (
            "\n".join(lines[:max_lines])
            + f"\n... ({len(lines) - max_lines} more lines)"
        )
    return code


def print_result_details(result: ProgramResult, show_js: bool = False):
    """Print detailed information about a failed program."""
    print(f"\n{'=' * 80}")
    print(f"PROGRAM: {result.filename}")
    print(f"STATUS: {result.status.value}")
    print("=" * 80)

    if result.status == Status.COMPILE_ERROR:
        print("\n--- COMPILE ERROR ---")
        print(f"Error: {result.compile_error}")
        if result.compile_traceback:
            print("\nTraceback:")
            print(result.compile_traceback)

    else:
        # Show JS code if requested
        if show_js and result.js_code:
            print("\n--- GENERATED JAVASCRIPT ---")
            print(format_code_block(result.js_code, 100))

        # QuickJS results
        if not result.quickjs_success:
            print("\n--- QUICKJS FAILURE ---")
            print(f"Return code: {result.quickjs_returncode}")
            print(f"Error: {result.quickjs_error}")
            if result.quickjs_stderr:
                print(f"Stderr:\n{result.quickjs_stderr}")
            if result.quickjs_stdout:
                print(f"Stdout (before error):\n{result.quickjs_stdout}")

        # Node.js results
        if not result.node_success:
            print("\n--- NODE.JS FAILURE ---")
            print(f"Return code: {result.node_returncode}")
            print(f"Error: {result.node_error}")
            if result.node_stderr:
                print(f"Stderr:\n{format_code_block(result.node_stderr, 30)}")
            if result.node_stdout:
                print(f"Stdout (before error):\n{result.node_stdout}")

        # Output mismatch
        if result.output_mismatch:
            print("\n--- OUTPUT MISMATCH ---")
            print("Node.js output:")
            print(result.node_stdout if result.node_stdout else "(no output)")
            print("\nPython output:")
            print(result.python_stdout if result.python_stdout else "(no output)")
        # Python reference
        elif result.python_success:
            print("\n--- PYTHON REFERENCE OUTPUT ---")
            print(result.python_stdout if result.python_stdout else "(no output)")
        elif result.python_stderr:
            print("\n--- PYTHON ALSO FAILED ---")
            print(result.python_stderr)


def print_summary(results: list[ProgramResult]):
    """Print summary statistics."""
    total = len(results)

    compile_errors = [r for r in results if r.status == Status.COMPILE_ERROR]
    compile_timeouts = [r for r in results if r.status == Status.COMPILE_TIMEOUT]
    quickjs_errors = [r for r in results if r.status == Status.QUICKJS_ERROR]
    quickjs_timeouts = [r for r in results if r.status == Status.QUICKJS_TIMEOUT]
    node_errors = [r for r in results if r.status == Status.NODE_ERROR]
    node_timeouts = [r for r in results if r.status == Status.NODE_TIMEOUT]
    output_mismatches = [r for r in results if r.status == Status.OUTPUT_MISMATCH]
    successes = [r for r in results if r.status == Status.SUCCESS]

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    print(f"\nTotal programs tested: {total}")
    print(f"  Fully successful: {len(successes)} ({100 * len(successes) / total:.1f}%)")
    print(f"  Compile errors: {len(compile_errors)}")
    print(f"  Compile timeouts: {len(compile_timeouts)}")
    print(f"  QuickJS errors: {len(quickjs_errors)}")
    print(f"  QuickJS timeouts: {len(quickjs_timeouts)}")
    print(f"  Node.js errors: {len(node_errors)}")
    print(f"  Node.js timeouts: {len(node_timeouts)}")
    print(f"  Output mismatches: {len(output_mismatches)}")

    # Categorize compile errors
    if compile_errors:
        print("\n" + "-" * 40)
        print("COMPILE ERRORS BY TYPE:")
        print("-" * 40)
        error_types: dict[str, list[str]] = {}
        for r in compile_errors:
            # Extract error type from message
            err = r.compile_error
            if ":" in err:
                err_type = err.split(":")[0].strip()
            else:
                err_type = err[:50]
            error_types.setdefault(err_type, []).append(r.filename)

        for err_type, files in sorted(error_types.items()):
            print(f"\n  {err_type} ({len(files)} files):")
            for f in sorted(files)[:5]:
                print(f"    - {f}")
            if len(files) > 5:
                print(f"    ... and {len(files) - 5} more")

    # Show compile timeouts
    if compile_timeouts:
        print("\n" + "-" * 40)
        print("COMPILE TIMEOUTS (hangs/memory exhaustion):")
        print("-" * 40)
        for r in sorted(compile_timeouts, key=lambda x: x.filename):
            print(f"  - {r.filename}")

    # Show QuickJS errors summary
    if quickjs_errors:
        print("\n" + "-" * 40)
        print("QUICKJS ERRORS BY TYPE:")
        print("-" * 40)
        error_types: dict[str, list[str]] = {}
        for r in quickjs_errors:
            err = r.quickjs_error
            if ":" in err:
                err_type = err.split(":")[0].strip()
            else:
                err_type = err[:50] if err else "Unknown"
            error_types.setdefault(err_type, []).append(r.filename)

        for err_type, files in sorted(error_types.items()):
            print(f"\n  {err_type} ({len(files)} files):")
            for f in sorted(files)[:5]:
                print(f"    - {f}")
            if len(files) > 5:
                print(f"    ... and {len(files) - 5} more")

    # Show Node.js errors summary
    if node_errors:
        print("\n" + "-" * 40)
        print("NODE.JS ERRORS BY TYPE:")
        print("-" * 40)
        error_types: dict[str, list[str]] = {}
        for r in node_errors:
            err = r.node_error
            if ":" in err:
                err_type = err.split(":")[0].strip()
            else:
                err_type = err[:50] if err else "Unknown"
            error_types.setdefault(err_type, []).append(r.filename)

        for err_type, files in sorted(error_types.items()):
            print(f"\n  {err_type} ({len(files)} files):")
            for f in sorted(files)[:5]:
                print(f"    - {f}")
            if len(files) > 5:
                print(f"    ... and {len(files) - 5} more")


def print_full_report(results: list[ProgramResult], show_js: bool = False):
    """Print detailed report for all failures."""
    failures = [r for r in results if r.status != Status.SUCCESS]

    if not failures:
        print("\n" + "=" * 80)
        print("ALL PROGRAMS PASSED!")
        print("=" * 80)
        return

    print("\n" + "=" * 80)
    print(f"DETAILED FAILURE REPORT ({len(failures)} failures)")
    print("=" * 80)

    # Group by status
    by_status = {}
    for r in failures:
        by_status.setdefault(r.status, []).append(r)

    # Print compile timeouts first (most severe - hangs the compiler)
    if Status.COMPILE_TIMEOUT in by_status:
        print("\n\n" + "#" * 80)
        print("# COMPILE TIMEOUTS (hangs/memory exhaustion)")
        print("#" * 80)
        for r in sorted(by_status[Status.COMPILE_TIMEOUT], key=lambda x: x.filename):
            print_result_details(r, show_js)

    # Print compile errors
    if Status.COMPILE_ERROR in by_status:
        print("\n\n" + "#" * 80)
        print("# COMPILE ERRORS")
        print("#" * 80)
        for r in sorted(by_status[Status.COMPILE_ERROR], key=lambda x: x.filename):
            print_result_details(r, show_js)

    # Then QuickJS errors
    if Status.QUICKJS_ERROR in by_status:
        print("\n\n" + "#" * 80)
        print("# QUICKJS RUNTIME ERRORS")
        print("#" * 80)
        for r in sorted(by_status[Status.QUICKJS_ERROR], key=lambda x: x.filename):
            print_result_details(r, show_js)

    # Then Node errors
    if Status.NODE_ERROR in by_status:
        print("\n\n" + "#" * 80)
        print("# NODE.JS RUNTIME ERRORS")
        print("#" * 80)
        for r in sorted(by_status[Status.NODE_ERROR], key=lambda x: x.filename):
            print_result_details(r, show_js)

    # Output mismatches
    if Status.OUTPUT_MISMATCH in by_status:
        print("\n\n" + "#" * 80)
        print("# OUTPUT MISMATCHES (JS output differs from Python)")
        print("#" * 80)
        for r in sorted(by_status[Status.OUTPUT_MISMATCH], key=lambda x: x.filename):
            print_result_details(r, show_js)

    # Timeouts
    for status in [Status.QUICKJS_TIMEOUT, Status.NODE_TIMEOUT]:
        if status in by_status:
            print(f"\n\n{'#' * 80}")
            print(f"# {status.value.upper()}")
            print("#" * 80)
            for r in sorted(by_status[status], key=lambda x: x.filename):
                print_result_details(r, show_js)


def save_results_json(results: list[ProgramResult], output_path: Path):
    """Save results to JSON for further analysis."""
    data = []
    for r in results:
        data.append(
            {
                "filename": r.filename,
                "status": r.status.value,
                "compile_success": r.compile_success,
                "compile_error": r.compile_error,
                "quickjs_success": r.quickjs_success,
                "quickjs_error": r.quickjs_error,
                "node_success": r.node_success,
                "node_error": r.node_error,
                "python_success": r.python_success,
                "output_mismatch": r.output_mismatch,
            }
        )

    output_path.write_text(json.dumps(data, indent=2))
    print(f"\nResults saved to: {output_path}")


def generate_denylist(results: list[ProgramResult]) -> str:
    """Generate a DENY_LIST in the format used by test_all.py."""
    # Group failures by status
    compile_timeouts = [r for r in results if r.status == Status.COMPILE_TIMEOUT]
    compile_errors = [r for r in results if r.status == Status.COMPILE_ERROR]
    quickjs_timeouts = [r for r in results if r.status == Status.QUICKJS_TIMEOUT]
    quickjs_errors = [r for r in results if r.status == Status.QUICKJS_ERROR]
    node_timeouts = [r for r in results if r.status == Status.NODE_TIMEOUT]
    node_errors = [r for r in results if r.status == Status.NODE_ERROR]
    output_mismatches = [r for r in results if r.status == Status.OUTPUT_MISMATCH]

    lines = ["DENY_LIST = {"]

    # Compile timeouts
    if compile_timeouts:
        lines.append("    # Compilation timeouts (hangs or memory exhaustion)")
        for r in sorted(compile_timeouts, key=lambda x: x.filename):
            lines.append(f'    "{r.filename}",')

    # Compile errors - group by error type
    if compile_errors:
        lines.append("    #")
        lines.append("    # Compilation errors")
        error_groups: dict[str, list[ProgramResult]] = {}
        for r in compile_errors:
            err = r.compile_error
            if ":" in err:
                err_type = err.split(":")[0].strip()
            else:
                err_type = "Other"
            error_groups.setdefault(err_type, []).append(r)

        for err_type, group in sorted(error_groups.items()):
            lines.append(f"    # {err_type}")
            for r in sorted(group, key=lambda x: x.filename):
                # Truncate long error messages
                short_err = r.compile_error[:60] + "..." if len(r.compile_error) > 60 else r.compile_error
                lines.append(f'    "{r.filename}",  # {short_err}')

    # QuickJS timeouts
    if quickjs_timeouts:
        lines.append("    #")
        lines.append("    # QuickJS execution timeouts")
        for r in sorted(quickjs_timeouts, key=lambda x: x.filename):
            lines.append(f'    "{r.filename}",')

    # QuickJS errors - group by error type
    if quickjs_errors:
        lines.append("    #")
        lines.append("    # QuickJS runtime errors")
        error_groups: dict[str, list[ProgramResult]] = {}
        for r in quickjs_errors:
            err = r.quickjs_error
            if ":" in err:
                err_type = err.split(":")[0].strip()
            else:
                err_type = "Other"
            error_groups.setdefault(err_type, []).append(r)

        for err_type, group in sorted(error_groups.items()):
            lines.append(f"    # {err_type}")
            for r in sorted(group, key=lambda x: x.filename):
                short_err = r.quickjs_error[:60] + "..." if len(r.quickjs_error) > 60 else r.quickjs_error
                lines.append(f'    "{r.filename}",  # {short_err}')

    # Node.js timeouts
    if node_timeouts:
        lines.append("    #")
        lines.append("    # Node.js execution timeouts")
        for r in sorted(node_timeouts, key=lambda x: x.filename):
            lines.append(f'    "{r.filename}",')

    # Node.js errors - group by error type
    if node_errors:
        lines.append("    #")
        lines.append("    # Node.js runtime errors")
        error_groups: dict[str, list[ProgramResult]] = {}
        for r in node_errors:
            err = r.node_error
            if ":" in err:
                err_type = err.split(":")[0].strip()
            else:
                err_type = "Other"
            error_groups.setdefault(err_type, []).append(r)

        for err_type, group in sorted(error_groups.items()):
            lines.append(f"    # {err_type}")
            for r in sorted(group, key=lambda x: x.filename):
                short_err = r.node_error[:60] + "..." if len(r.node_error) > 60 else r.node_error
                lines.append(f'    "{r.filename}",  # {short_err}')

    # Output mismatches (JS output differs from Python)
    if output_mismatches:
        lines.append("    #")
        lines.append("    # Output mismatches (JS output differs from Python)")
        for r in sorted(output_mismatches, key=lambda x: x.filename):
            lines.append(f'    "{r.filename}",')

    lines.append("}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Test MicroPython programs through the Prescrypt compiler"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show progress for each program"
    )
    parser.add_argument(
        "--filter",
        "-f",
        type=str,
        default="",
        help="Only test programs matching this pattern",
    )
    parser.add_argument(
        "--show-js",
        action="store_true",
        help="Show generated JavaScript in failure reports",
    )
    parser.add_argument("--json", type=str, help="Save results to JSON file")
    parser.add_argument(
        "--no-python", action="store_true", help="Skip Python reference execution"
    )
    parser.add_argument(
        "--only-failures",
        action="store_true",
        help="Only show detailed report (skip per-program progress)",
    )
    parser.add_argument(
        "--compile-timeout",
        type=int,
        default=COMPILE_TIMEOUT,
        help=f"Timeout for compilation in seconds (default: {COMPILE_TIMEOUT})",
    )
    parser.add_argument(
        "--run-timeout",
        type=int,
        default=TIMEOUT,
        help=f"Timeout for JS execution in seconds (default: {TIMEOUT})",
    )
    parser.add_argument(
        "--create-denylist",
        action="store_true",
        help="Output a DENY_LIST for test_all.py (organized by error type)",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Quiet mode: only output total programs and failures count",
    )
    parser.add_argument(
        "--update-denylist",
        action="store_true",
        help="Test only programs in current denylist, show newly passing programs and updated denylist",
    )

    args = parser.parse_args()

    # Collect program files
    program_files = sorted(
        f for f in PROGRAMS_DIR.iterdir() if f.is_file() and f.suffix == ".py"
    )

    # Load current denylist if --update-denylist is used
    current_denylist: set[str] = set()
    if args.update_denylist:
        try:
            from .denylist import DENY_LIST
            current_denylist = DENY_LIST
        except ImportError:
            # Try direct import for standalone execution
            import sys
            sys.path.insert(0, str(Path(__file__).parent))
            from denylist import DENY_LIST
            current_denylist = DENY_LIST
        # Filter to only test programs in the denylist
        program_files = [f for f in program_files if f.name in current_denylist]

    # Apply filter
    if args.filter:
        program_files = [f for f in program_files if args.filter in f.name]

    if not program_files:
        if not args.quiet:
            print("No programs found matching criteria")
        return

    if not args.quiet:
        print(f"Testing {len(program_files)} programs...\n")

    results: list[ProgramResult] = []

    for i, source_path in enumerate(program_files, 1):
        if not args.quiet and args.verbose and not args.only_failures:
            print(
                f"[{i}/{len(program_files)}] {source_path.name}...", end=" ", flush=True
            )

        result = test_program(
            source_path,
            run_python_ref=not args.no_python,
            compile_timeout=args.compile_timeout,
            run_timeout=args.run_timeout,
        )
        results.append(result)

        if not args.quiet:
            if args.verbose and not args.only_failures:
                if result.status == Status.SUCCESS:
                    print("OK")
                else:
                    print(f"FAILED ({result.status.value})")
            elif not args.only_failures:
                # Show dots for progress
                if result.status == Status.SUCCESS:
                    print(".", end="", flush=True)
                else:
                    print("F", end="", flush=True)
                if i % 50 == 0:
                    print(f" [{i}]")

    if not args.quiet and not args.verbose and not args.only_failures:
        print()  # Newline after dots

    # Quiet mode: just print totals
    if args.quiet:
        total = len(results)
        failures = sum(1 for r in results if r.status != Status.SUCCESS)
        print(f"{failures}/{total}")
        return

    # Print summary
    print_summary(results)

    # Print full report (unless --create-denylist is set, which is more concise)
    if not args.create_denylist:
        print_full_report(results, show_js=args.show_js)

    # Save to JSON if requested
    if args.json:
        save_results_json(results, Path(args.json))

    # Generate denylist if requested
    if args.create_denylist:
        print("\n" + "=" * 80)
        print("GENERATED DENY_LIST")
        print("=" * 80)
        print()
        print(generate_denylist(results))

    # Update denylist mode: show newly passing and updated denylist
    if args.update_denylist:
        # Find programs that now pass (were in denylist, now succeed)
        now_passing = [r for r in results if r.status == Status.SUCCESS]
        still_failing = [r for r in results if r.status != Status.SUCCESS]

        print("\n" + "=" * 80)
        print("NEWLY PASSING PROGRAMS")
        print("=" * 80)
        if now_passing:
            print(f"\n{len(now_passing)} program(s) now pass and can be removed from denylist:\n")
            for r in sorted(now_passing, key=lambda x: x.filename):
                print(f"  - {r.filename}")
        else:
            print("\nNo programs are newly passing.")

        print("\n" + "=" * 80)
        print("UPDATED DENY_LIST")
        print("=" * 80)
        print(f"\n# {len(still_failing)} programs still failing\n")
        print(generate_denylist(still_failing))


if __name__ == "__main__":
    main()
