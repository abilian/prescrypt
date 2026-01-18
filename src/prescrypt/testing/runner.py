"""Compilation and execution helpers for test programs.

This module provides functions to compile Python to JavaScript and run
the resulting code in various JavaScript runtimes.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from .models import Config, Program, Status, TestResult
from .paths import PROJECT_ROOT

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

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
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

COMPILE_TIMEOUT = 5
RUNTIME_TIMEOUT = 10
COMPILE_MEMORY_LIMIT = 512 * 1024 * 1024


def _set_memory_limit():
    """Set memory limit for the subprocess."""
    try:
        import resource

        resource.setrlimit(
            resource.RLIMIT_AS, (COMPILE_MEMORY_LIMIT, COMPILE_MEMORY_LIMIT)
        )
    except (ValueError, OSError, AttributeError):
        pass


def compile_program(
    source_path: Path, timeout: int = COMPILE_TIMEOUT
) -> tuple[str, str, str, str, int]:
    """Compile a Python file to JavaScript in a separate subprocess.

    Returns:
        (status, js_code, error_message, traceback, time_ms)
        status is one of: "success", "error", "timeout"
    """
    # Create the helper script file
    script_path = PROJECT_ROOT / "scripts" / "_compile_helper.py"

    try:
        # Write the helper script if it doesn't exist or is outdated
        if not script_path.exists():
            script_path.write_text(_COMPILE_SCRIPT)

        start_time = time.time()

        # Start the compilation in a subprocess with its own process group
        process = subprocess.Popen(
            [sys.executable, str(script_path), str(source_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
            preexec_fn=_set_memory_limit,  # noqa: PLW1509
        )

        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(process.pid), signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                process.kill()
            process.wait()
            elapsed_ms = int((time.time() - start_time) * 1000)
            return (
                "timeout",
                "",
                f"Compilation timed out after {timeout}s",
                "",
                elapsed_ms,
            )

        elapsed_ms = int((time.time() - start_time) * 1000)

        if process.returncode != 0:
            if process.returncode == -signal.SIGKILL:
                return "timeout", "", "Compilation killed (likely OOM)", "", elapsed_ms
            return (
                "error",
                "",
                f"Subprocess error (exit {process.returncode}): {stderr[:500]}",
                "",
                elapsed_ms,
            )

        # Parse the JSON output
        try:
            data = json.loads(stdout)
            return (
                data["status"],
                data["js_code"],
                data["error"],
                data["traceback"],
                elapsed_ms,
            )
        except json.JSONDecodeError:
            return (
                "error",
                "",
                f"Failed to parse compiler output: {stdout[:200]}",
                "",
                elapsed_ms,
            )

    except Exception as e:
        return "error", "", f"Compilation failed: {e}", "", 0


def run_javascript(
    js_code: str, runtime: str = "node", timeout: int = RUNTIME_TIMEOUT
) -> tuple[str, str, str, int]:
    """Run JavaScript code with specified runtime.

    Args:
        js_code: JavaScript code to execute
        runtime: "node" or "quickjs"
        timeout: timeout in seconds

    Returns:
        (status, stdout, error_message, time_ms)
        status is one of: "success", "error", "timeout"
    """
    cmd = ["node"] if runtime == "node" else ["qjs"]

    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
            f.write(js_code)
            temp_path = Path(f.name)

        try:
            start_time = time.time()

            process = subprocess.Popen(
                cmd + [str(temp_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                start_new_session=True,
            )

            try:
                stdout, stderr = process.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                except (ProcessLookupError, PermissionError):
                    process.kill()
                process.wait()
                elapsed_ms = int((time.time() - start_time) * 1000)
                return "timeout", "", f"Timeout after {timeout}s", elapsed_ms

            elapsed_ms = int((time.time() - start_time) * 1000)

            if process.returncode == 0:
                return "success", stdout.strip(), "", elapsed_ms
            else:
                # Extract error message from stderr
                lines = [ln for ln in stderr.strip().split("\n") if ln.strip()]
                error = ""
                for line in lines:
                    if "Error:" in line or "Error " in line:
                        error = line.strip()
                        break
                if not error:
                    error = lines[0] if lines else f"Exit code {process.returncode}"
                return "error", stdout.strip(), error, elapsed_ms

        finally:
            temp_path.unlink()

    except FileNotFoundError:
        return "error", "", f"{runtime} not found in PATH", 0
    except Exception as e:
        return "error", "", str(e), 0


def run_program_test(
    program: Program,
    config: Config,
    compile_timeout: int = COMPILE_TIMEOUT,
    run_timeout: int = RUNTIME_TIMEOUT,
) -> list[TestResult]:
    """Test a program through the full pipeline.

    Returns a list of TestResult objects (one per runtime).
    """
    results = []
    source_path = program.full_path

    # Step 1: Compile
    compile_status, js_code, compile_err, _compile_tb, compile_time = compile_program(
        source_path, compile_timeout
    )

    if compile_status == "timeout":
        for runtime in config.runtimes:
            results.append(
                TestResult(
                    program_path=program.path,
                    status=Status.COMPILE_TIMEOUT,
                    compile_time_ms=compile_time,
                    error_message=compile_err,
                    runtime=runtime,
                )
            )
        return results

    if compile_status == "error":
        for runtime in config.runtimes:
            results.append(
                TestResult(
                    program_path=program.path,
                    status=Status.COMPILE_FAIL,
                    compile_time_ms=compile_time,
                    error_message=compile_err,
                    runtime=runtime,
                )
            )
        return results

    # Step 2: Run with each runtime and compare to Python output
    python_output = program.cpython_output.strip() if program.cpython_output else ""

    for runtime in config.runtimes:
        run_status, js_stdout, run_err, run_time = run_javascript(
            js_code, runtime, run_timeout
        )

        if run_status == "timeout":
            results.append(
                TestResult(
                    program_path=program.path,
                    status=Status.RUNTIME_TIMEOUT,
                    compile_time_ms=compile_time,
                    runtime_ms=run_time,
                    error_message=run_err,
                    runtime=runtime,
                )
            )
        elif run_status == "error":
            # Extract error type from error message
            error_type = None
            if ":" in run_err:
                error_type = run_err.split(":")[0].strip()
            results.append(
                TestResult(
                    program_path=program.path,
                    status=Status.RUNTIME_ERROR,
                    compile_time_ms=compile_time,
                    runtime_ms=run_time,
                    js_output=js_stdout,
                    error_message=run_err,
                    error_type=error_type,
                    runtime=runtime,
                )
            )
        else:
            # Compare output
            if js_stdout == python_output:
                results.append(
                    TestResult(
                        program_path=program.path,
                        status=Status.RUNTIME_PASS,
                        compile_time_ms=compile_time,
                        runtime_ms=run_time,
                        js_output=js_stdout,
                        runtime=runtime,
                    )
                )
            else:
                results.append(
                    TestResult(
                        program_path=program.path,
                        status=Status.RUNTIME_FAIL,
                        compile_time_ms=compile_time,
                        runtime_ms=run_time,
                        js_output=js_stdout,
                        error_message=f"Output mismatch: expected '{python_output[:100]}...', got '{js_stdout[:100]}...'",
                        runtime=runtime,
                    )
                )

    return results
