#!/usr/bin/env python3
"""Test Manager for Prescrypt end-to-end tests.

This script manages the test suite for Prescrypt, tracking test programs,
their status, and results over time in a SQLite database.

Usage:
    ./scripts/test_manager.py discover          # Find all test programs
    ./scripts/test_manager.py validate-cpython  # Check which run on CPython
    ./scripts/test_manager.py classify          # Full classification pipeline
    ./scripts/test_manager.py run               # Run all eligible tests
    ./scripts/test_manager.py status            # Quick summary
    ./scripts/test_manager.py report            # Generate HTML report
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sqlite3
import subprocess
import sys
import tempfile
import time
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Try to import tomllib (Python 3.11+) or fall back to tomli
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
PROGRAMS_DIR = PROJECT_ROOT / "programs"
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_PATH = DATA_DIR / "test-results.db"
CONFIG_PATH = DATA_DIR / "test-config.toml"


# Status constants
class Status:
    # Discovery statuses
    DISCOVERED = "DISCOVERED"

    # CPython validation statuses
    CPYTHON_PASS = "CPYTHON_PASS"
    CPYTHON_FAIL = "CPYTHON_FAIL"
    CPYTHON_SKIP = "CPYTHON_SKIP"
    CPYTHON_TIMEOUT = "CPYTHON_TIMEOUT"

    # Compilation statuses
    COMPILE_PASS = "COMPILE_PASS"
    COMPILE_FAIL = "COMPILE_FAIL"
    COMPILE_ERROR = "COMPILE_ERROR"
    COMPILE_TIMEOUT = "COMPILE_TIMEOUT"

    # Runtime statuses
    RUNTIME_PASS = "RUNTIME_PASS"
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

    @property
    def full_path(self) -> Path:
        return PROGRAMS_DIR / self.path

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


@dataclass
class Config:
    """Configuration loaded from test-config.toml."""

    timeout: int = 10
    runtimes: list[str] = None
    python: str = "python3"
    programs_dir: str = "programs"
    include_patterns: list[str] = None
    exclude_patterns: list[str] = None
    micropython_only: list[str] = None
    unsupported_features: list[str] = None
    manual_skip: list[str] = None
    force_include: list[str] = None
    known_failures: list[str] = None

    def __post_init__(self):
        if self.runtimes is None:
            self.runtimes = ["quickjs", "node"]
        if self.include_patterns is None:
            self.include_patterns = ["**/*.py"]
        if self.exclude_patterns is None:
            self.exclude_patterns = ["**/__pycache__/**", "**/_*.py"]
        if self.micropython_only is None:
            self.micropython_only = []
        if self.unsupported_features is None:
            self.unsupported_features = []
        if self.manual_skip is None:
            self.manual_skip = []
        if self.force_include is None:
            self.force_include = []
        if self.known_failures is None:
            self.known_failures = []

    @classmethod
    def load(cls, path: Path | None = None) -> Config:
        """Load configuration from TOML file."""
        if path is None:
            path = CONFIG_PATH

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


class TestDatabase:
    """SQLite database for storing test results."""

    SCHEMA = """
    -- Test runs
    CREATE TABLE IF NOT EXISTS runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        started_at TIMESTAMP NOT NULL,
        finished_at TIMESTAMP,
        git_commit TEXT,
        git_branch TEXT,
        python_version TEXT,
        prescrypt_version TEXT,
        total_programs INTEGER,
        passed INTEGER,
        failed INTEGER,
        skipped INTEGER,
        errors INTEGER,
        notes TEXT
    );

    -- Test programs
    CREATE TABLE IF NOT EXISTS programs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT UNIQUE NOT NULL,
        source TEXT,
        first_seen_run INTEGER,
        last_seen_run INTEGER,
        cpython_status TEXT,
        cpython_output TEXT,
        cpython_error TEXT,
        cpython_hash TEXT,
        manual_skip BOOLEAN DEFAULT FALSE,
        skip_reason TEXT,
        FOREIGN KEY (first_seen_run) REFERENCES runs(id),
        FOREIGN KEY (last_seen_run) REFERENCES runs(id)
    );

    -- Test results
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER NOT NULL,
        program_id INTEGER NOT NULL,
        status TEXT NOT NULL,
        compile_time_ms INTEGER,
        runtime_ms INTEGER,
        js_output TEXT,
        error_message TEXT,
        error_type TEXT,
        runtime TEXT,
        FOREIGN KEY (run_id) REFERENCES runs(id),
        FOREIGN KEY (program_id) REFERENCES programs(id)
    );

    -- Regressions tracking
    CREATE TABLE IF NOT EXISTS regressions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER NOT NULL,
        program_id INTEGER NOT NULL,
        previous_status TEXT,
        new_status TEXT,
        is_improvement BOOLEAN,
        FOREIGN KEY (run_id) REFERENCES runs(id),
        FOREIGN KEY (program_id) REFERENCES programs(id)
    );

    -- Indexes for common queries
    CREATE INDEX IF NOT EXISTS idx_programs_path ON programs(path);
    CREATE INDEX IF NOT EXISTS idx_programs_source ON programs(source);
    CREATE INDEX IF NOT EXISTS idx_programs_cpython_status ON programs(cpython_status);
    CREATE INDEX IF NOT EXISTS idx_results_run_id ON results(run_id);
    CREATE INDEX IF NOT EXISTS idx_results_program_id ON results(program_id);
    CREATE INDEX IF NOT EXISTS idx_results_status ON results(status);
    """

    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or DATABASE_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        """Initialize database schema."""
        self.conn.executescript(self.SCHEMA)
        self.conn.commit()

    def close(self):
        """Close database connection."""
        self.conn.close()

    # Program management

    def get_program(self, path: str) -> Program | None:
        """Get a program by path."""
        cursor = self.conn.execute(
            "SELECT * FROM programs WHERE path = ?",
            (path,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_program(row)

    def get_all_programs(self) -> list[Program]:
        """Get all programs."""
        cursor = self.conn.execute("SELECT * FROM programs ORDER BY path")
        return [self._row_to_program(row) for row in cursor.fetchall()]

    def get_programs_by_status(
        self, statuses: list[str], exclude_manual_skip: bool = True
    ) -> list[Program]:
        """Get programs by CPython status."""
        placeholders = ",".join("?" * len(statuses))
        query = f"SELECT * FROM programs WHERE cpython_status IN ({placeholders})"
        if exclude_manual_skip:
            query += " AND manual_skip = FALSE"
        query += " ORDER BY path"
        cursor = self.conn.execute(query, statuses)
        return [self._row_to_program(row) for row in cursor.fetchall()]

    def upsert_program(self, program: Program) -> int:
        """Insert or update a program."""
        cursor = self.conn.execute(
            """
            INSERT INTO programs (path, source, first_seen_run, last_seen_run,
                                  cpython_status, cpython_output, cpython_error,
                                  manual_skip, skip_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(path) DO UPDATE SET
                source = excluded.source,
                last_seen_run = excluded.last_seen_run,
                cpython_status = COALESCE(excluded.cpython_status, cpython_status),
                cpython_output = COALESCE(excluded.cpython_output, cpython_output),
                cpython_error = COALESCE(excluded.cpython_error, cpython_error),
                manual_skip = excluded.manual_skip,
                skip_reason = excluded.skip_reason
            """,
            (
                program.path,
                program.source,
                program.first_seen_run,
                program.last_seen_run,
                program.cpython_status,
                program.cpython_output,
                program.cpython_error,
                program.manual_skip,
                program.skip_reason,
            ),
        )
        self.conn.commit()
        return cursor.lastrowid

    def update_cpython_status(
        self,
        path: str,
        status: str,
        output: str | None = None,
        error: str | None = None,
    ):
        """Update CPython validation status for a program."""
        output_hash = hashlib.md5(output.encode()).hexdigest() if output else None
        self.conn.execute(
            """
            UPDATE programs
            SET cpython_status = ?, cpython_output = ?, cpython_error = ?, cpython_hash = ?
            WHERE path = ?
            """,
            (status, output, error, output_hash, path),
        )
        self.conn.commit()

    def _row_to_program(self, row: sqlite3.Row) -> Program:
        """Convert database row to Program object."""
        return Program(
            id=row["id"],
            path=row["path"],
            source=row["source"],
            first_seen_run=row["first_seen_run"],
            last_seen_run=row["last_seen_run"],
            cpython_status=row["cpython_status"],
            cpython_output=row["cpython_output"],
            cpython_error=row["cpython_error"],
            manual_skip=bool(row["manual_skip"]),
            skip_reason=row["skip_reason"],
        )

    # Run management

    def create_run(self, notes: str | None = None) -> int:
        """Create a new test run."""
        git_commit = self._get_git_commit()
        git_branch = self._get_git_branch()
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

        cursor = self.conn.execute(
            """
            INSERT INTO runs (started_at, git_commit, git_branch, python_version, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (datetime.now(), git_commit, git_branch, python_version, notes),
        )
        self.conn.commit()
        return cursor.lastrowid

    def finish_run(
        self,
        run_id: int,
        total: int,
        passed: int,
        failed: int,
        skipped: int,
        errors: int,
    ):
        """Mark a run as finished with summary stats."""
        self.conn.execute(
            """
            UPDATE runs
            SET finished_at = ?, total_programs = ?, passed = ?, failed = ?, skipped = ?, errors = ?
            WHERE id = ?
            """,
            (datetime.now(), total, passed, failed, skipped, errors, run_id),
        )
        self.conn.commit()

    def get_latest_run(self) -> dict | None:
        """Get the most recent run."""
        cursor = self.conn.execute("SELECT * FROM runs ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        return dict(row) if row else None

    def _get_git_commit(self) -> str | None:
        """Get current git commit hash."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT,
            )
            return result.stdout.strip()[:12] if result.returncode == 0 else None
        except Exception:
            return None

    def _get_git_branch(self) -> str | None:
        """Get current git branch."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT,
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except Exception:
            return None

    # Results management

    def add_result(self, run_id: int, program_id: int, result: TestResult):
        """Add a test result."""
        self.conn.execute(
            """
            INSERT INTO results (run_id, program_id, status, compile_time_ms,
                                runtime_ms, js_output, error_message, error_type, runtime)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                program_id,
                result.status,
                result.compile_time_ms,
                result.runtime_ms,
                result.js_output,
                result.error_message,
                result.error_type,
                result.runtime,
            ),
        )
        self.conn.commit()

    # Statistics

    def get_status_counts(self) -> dict[str, int]:
        """Get counts of programs by CPython status."""
        cursor = self.conn.execute(
            """
            SELECT cpython_status, COUNT(*) as count
            FROM programs
            GROUP BY cpython_status
            """
        )
        return {
            row["cpython_status"] or "UNKNOWN": row["count"]
            for row in cursor.fetchall()
        }


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


# Compilation and execution helpers

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
    import json
    import signal

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
            preexec_fn=_set_memory_limit,
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
    import signal

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
                lines = [l for l in stderr.strip().split("\n") if l.strip()]
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


def test_program_full(
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
    compile_status, js_code, compile_err, compile_tb, compile_time = compile_program(
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


# CLI Commands


def cmd_discover(args, config: Config, db: TestDatabase):
    """Discover all test programs and add them to the database."""
    print("Discovering test programs...")

    # Create a run for tracking when programs were discovered
    run_id = db.create_run(notes="Discovery run")

    count = 0
    new_count = 0

    for rel_path, source in discover_programs(config):
        existing = db.get_program(rel_path)

        if existing is None:
            new_count += 1
            first_seen = run_id
        else:
            first_seen = existing.first_seen_run

        program = Program(
            id=None,
            path=rel_path,
            source=source,
            first_seen_run=first_seen,
            last_seen_run=run_id,
            cpython_status=existing.cpython_status if existing else None,
            cpython_output=existing.cpython_output if existing else None,
            cpython_error=existing.cpython_error if existing else None,
            manual_skip=rel_path in config.manual_skip,
            skip_reason="Manual skip" if rel_path in config.manual_skip else None,
        )

        db.upsert_program(program)
        count += 1

        if args.verbose:
            status = "NEW" if existing is None else "updated"
            print(f"  [{status}] {rel_path}")

    print(f"\nDiscovered {count} programs ({new_count} new)")

    # Show breakdown by source
    programs = db.get_all_programs()
    sources = {}
    for p in programs:
        sources[p.source] = sources.get(p.source, 0) + 1

    print("\nBy source:")
    for source, count in sorted(sources.items()):
        print(f"  {source}: {count}")


def cmd_validate_cpython(args, config: Config, db: TestDatabase):
    """Validate which programs run on CPython."""
    programs = db.get_all_programs()

    if not programs:
        print("No programs found. Run 'discover' first.")
        return

    # Filter programs
    if args.only_new:
        programs = [p for p in programs if p.cpython_status is None]
    elif args.only_failed:
        programs = [p for p in programs if p.cpython_status == Status.CPYTHON_FAIL]

    if args.filter:
        import fnmatch

        programs = [p for p in programs if fnmatch.fnmatch(p.path, args.filter)]

    print(f"Validating {len(programs)} programs on CPython...")

    stats = {
        Status.CPYTHON_PASS: 0,
        Status.CPYTHON_FAIL: 0,
        Status.CPYTHON_SKIP: 0,
        Status.CPYTHON_TIMEOUT: 0,
    }

    for i, program in enumerate(programs):
        if program.manual_skip:
            continue

        full_path = PROGRAMS_DIR / program.path

        if not full_path.exists():
            print(f"  Warning: {program.path} not found")
            continue

        status, output, error = validate_cpython(full_path, config)
        db.update_cpython_status(program.path, status, output, error)
        stats[status] = stats.get(status, 0) + 1

        if args.verbose:
            symbol = (
                "✓"
                if status == Status.CPYTHON_PASS
                else "✗"
                if status == Status.CPYTHON_FAIL
                else "○"
            )
            print(f"  [{symbol}] {program.path}")
        else:
            # Progress indicator
            if (i + 1) % 50 == 0:
                print(f"  ... {i + 1}/{len(programs)}")

    print("\nResults:")
    print(f"  PASS:    {stats.get(Status.CPYTHON_PASS, 0)}")
    print(f"  FAIL:    {stats.get(Status.CPYTHON_FAIL, 0)}")
    print(f"  SKIP:    {stats.get(Status.CPYTHON_SKIP, 0)}")
    print(f"  TIMEOUT: {stats.get(Status.CPYTHON_TIMEOUT, 0)}")


def cmd_status(args, config: Config, db: TestDatabase):
    """Show current status summary."""
    programs = db.get_all_programs()
    counts = db.get_status_counts()
    latest_run = db.get_latest_run()

    print("\nPrescrypt Test Suite Status")
    print("=" * 40)

    if latest_run:
        print(
            f"Git: {latest_run.get('git_branch', 'unknown')} @ {latest_run.get('git_commit', 'unknown')}"
        )
        print(
            f"Last run: #{latest_run.get('id')} at {latest_run.get('started_at', 'never')}"
        )

    print(f"\nPrograms: {len(programs)} total")

    if counts:
        print("\nBy CPython status:")
        for status in [
            Status.CPYTHON_PASS,
            Status.CPYTHON_FAIL,
            Status.CPYTHON_SKIP,
            Status.CPYTHON_TIMEOUT,
            "UNKNOWN",
        ]:
            count = counts.get(status, 0)
            if count > 0:
                print(f"  {status}: {count}")

    # Show by source
    sources = {}
    for p in programs:
        sources[p.source] = sources.get(p.source, 0) + 1

    if sources:
        print("\nBy source:")
        for source, count in sorted(sources.items()):
            print(f"  {source}: {count}")

    # Show latest run results
    if latest_run and latest_run.get("total_programs"):
        print(f"\nLatest Run Results (#{latest_run.get('id')}):")
        total = latest_run.get("total_programs", 0)
        passed = latest_run.get("passed", 0)
        failed = latest_run.get("failed", 0)
        skipped = latest_run.get("skipped", 0)
        errors = latest_run.get("errors", 0)

        if total > 0:
            print(f"  Tested:  {total}")
            print(f"  PASS:    {passed} ({100 * passed / total:.1f}%)")
            print(f"  FAIL:    {failed}")
            print(f"  SKIP:    {skipped}")
            print(f"  ERRORS:  {errors}")

        # Get error type breakdown from results table
        cursor = db.conn.execute(
            """
            SELECT error_type, COUNT(*) as count
            FROM results
            WHERE run_id = ? AND error_type IS NOT NULL
            GROUP BY error_type
            ORDER BY count DESC
            LIMIT 10
        """,
            (latest_run.get("id"),),
        )
        error_types = cursor.fetchall()

        if error_types:
            print("\n  Error types:")
            for row in error_types:
                print(f"    {row[0]}: {row[1]}")


def cmd_import_denylist(args, config: Config, db: TestDatabase):
    """Import programs from existing denylist files."""
    denylist_path = (
        PROJECT_ROOT / "tests" / "c_e2e" / "from_micropython" / "denylist.py"
    )

    if not denylist_path.exists():
        print(f"Denylist not found: {denylist_path}")
        return

    # Parse the denylist.py file
    import ast

    with open(denylist_path) as f:
        content = f.read()

    tree = ast.parse(content)

    deny_list = set()
    allow_list = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if target.id == "DENY_LIST" and isinstance(node.value, ast.Set):
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Constant):
                                deny_list.add(elt.value)
                    elif target.id == "ALLOW_LIST" and isinstance(node.value, ast.Set):
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Constant):
                                allow_list.add(elt.value)

    print(f"Found {len(deny_list)} entries in DENY_LIST")
    print(f"Found {len(allow_list)} entries in ALLOW_LIST")

    # Update programs in database
    for program_name in deny_list:
        if program_name in allow_list:
            continue

        # Find the program in database
        programs = db.get_all_programs()
        for p in programs:
            if p.name == program_name:
                db.conn.execute(
                    "UPDATE programs SET manual_skip = TRUE, skip_reason = 'Imported from denylist' WHERE path = ?",
                    (p.path,),
                )

    db.conn.commit()
    print("Denylist imported to database")


def cmd_run(args, config: Config, db: TestDatabase):
    """Run tests through the full pipeline."""
    import fnmatch

    # Get eligible programs (CPython PASS only, unless --all)
    if args.all:
        programs = db.get_all_programs()
    else:
        programs = db.get_programs_by_status([Status.CPYTHON_PASS])

    # Apply filters
    if args.only_failed:
        # Get programs that failed in the last run
        cursor = db.conn.execute("""
            SELECT DISTINCT p.path FROM programs p
            JOIN results r ON p.id = r.program_id
            WHERE r.run_id = (SELECT MAX(id) FROM runs)
            AND r.status NOT IN ('RUNTIME_PASS', 'COMPILE_PASS')
        """)
        failed_paths = {row[0] for row in cursor.fetchall()}
        programs = [p for p in programs if p.path in failed_paths]

    if args.filter:
        programs = [p for p in programs if fnmatch.fnmatch(p.path, args.filter)]

    # Exclude manual skips
    programs = [p for p in programs if not p.manual_skip]

    if not programs:
        print("No programs to test")
        return

    print(f"Running {len(programs)} programs...")
    print(f"Runtimes: {', '.join(config.runtimes)}")
    print()

    # Create a new run
    run_id = db.create_run(notes=f"Test run: {len(programs)} programs")

    # Statistics
    stats = {
        Status.RUNTIME_PASS: 0,
        Status.RUNTIME_FAIL: 0,
        Status.RUNTIME_ERROR: 0,
        Status.RUNTIME_TIMEOUT: 0,
        Status.COMPILE_FAIL: 0,
        Status.COMPILE_TIMEOUT: 0,
    }

    # Error categorization
    error_types: dict[str, list[str]] = {}

    for i, program in enumerate(programs):
        if args.verbose:
            print(f"[{i + 1}/{len(programs)}] {program.path}...", end=" ", flush=True)

        results = test_program_full(program, config)

        # Get program ID
        prog_row = db.conn.execute(
            "SELECT id FROM programs WHERE path = ?", (program.path,)
        ).fetchone()
        if prog_row:
            program_id = prog_row[0]
            for result in results:
                db.add_result(run_id, program_id, result)

        # Update stats (use first runtime for overall stats)
        if results:
            first_result = results[0]
            stats[first_result.status] = stats.get(first_result.status, 0) + 1

            # Track error types
            if first_result.error_type:
                error_types.setdefault(first_result.error_type, []).append(program.path)

            if args.verbose:
                if first_result.status == Status.RUNTIME_PASS:
                    print("PASS")
                else:
                    print(f"FAIL ({first_result.status})")
            else:
                # Progress dots
                if first_result.status == Status.RUNTIME_PASS:
                    print(".", end="", flush=True)
                else:
                    print("F", end="", flush=True)
                if (i + 1) % 50 == 0:
                    print(f" [{i + 1}]")

    if not args.verbose:
        print()  # Newline after dots

    # Calculate totals
    passed = stats.get(Status.RUNTIME_PASS, 0)
    failed = stats.get(Status.RUNTIME_FAIL, 0)
    errors = stats.get(Status.RUNTIME_ERROR, 0)
    timeouts = stats.get(Status.RUNTIME_TIMEOUT, 0) + stats.get(
        Status.COMPILE_TIMEOUT, 0
    )
    compile_fails = stats.get(Status.COMPILE_FAIL, 0)

    # Finish the run
    db.finish_run(
        run_id,
        total=len(programs),
        passed=passed,
        failed=failed + errors,
        skipped=compile_fails,
        errors=timeouts,
    )

    # Print summary
    print("\n" + "=" * 50)
    print(f"Run #{run_id} Complete")
    print("=" * 50)
    print(f"\nTotal programs: {len(programs)}")
    print(f"  PASS:          {passed} ({100 * passed / len(programs):.1f}%)")
    print(f"  FAIL:          {failed}")
    print(f"  RUNTIME_ERROR: {errors}")
    print(f"  COMPILE_FAIL:  {compile_fails}")
    print(f"  TIMEOUT:       {timeouts}")

    if error_types:
        print("\nError types:")
        for error_type, paths in sorted(error_types.items(), key=lambda x: -len(x[1])):
            print(f"  {error_type}: {len(paths)}")
            if args.verbose:
                for p in paths[:5]:
                    print(f"    - {p}")
                if len(paths) > 5:
                    print(f"    ... and {len(paths) - 5} more")


def cmd_report(args, config: Config, db: TestDatabase):
    """Generate HTML report for test results."""
    import html
    import re
    from collections import defaultdict

    run_id = args.run if hasattr(args, "run") and args.run else None

    if run_id is None:
        # Get latest run
        latest = db.get_latest_run()
        if not latest:
            print("No test runs found. Run 'test_manager.py run' first.")
            return
        run_id = latest["id"]

    # Get run info
    run = db.conn.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
    if not run:
        print(f"Run #{run_id} not found")
        return

    # Get all results for this run
    results = db.conn.execute(
        """
        SELECT r.*, p.path, p.source, p.cpython_output
        FROM results r
        JOIN programs p ON r.program_id = p.id
        WHERE r.run_id = ? AND r.runtime = 'node'
        ORDER BY r.status, p.path
    """,
        (run_id,),
    ).fetchall()

    # Categorize results
    by_status = defaultdict(list)
    for r in results:
        by_status[r["status"]].append(r)

    # Analyze errors for actionable insights
    reference_errors = defaultdict(list)  # missing_name -> [programs]
    type_errors = defaultdict(list)
    syntax_errors = defaultdict(list)
    compile_errors = defaultdict(list)
    output_mismatches = []

    for r in results:
        error_msg = r["error_message"] or ""
        path = r["path"]

        if r["status"] == Status.RUNTIME_ERROR:
            error_type = r["error_type"] or "Unknown"

            if "ReferenceError" in error_type:
                # Extract the undefined name
                match = re.search(r"'(\w+)'|(\w+) is not defined", error_msg)
                if match:
                    name = match.group(1) or match.group(2)
                    reference_errors[name].append(path)
                else:
                    reference_errors["_other_"].append(path)

            elif "TypeError" in error_type:
                # Categorize type errors
                if "not a function" in error_msg:
                    type_errors["not a function"].append((path, error_msg))
                elif "cannot read property" in error_msg.lower():
                    prop_match = re.search(r"property '(\w+)'", error_msg)
                    prop = prop_match.group(1) if prop_match else "unknown"
                    type_errors[f"missing property: {prop}"].append((path, error_msg))
                elif "not iterable" in error_msg:
                    type_errors["not iterable"].append((path, error_msg))
                elif "instanceof" in error_msg:
                    type_errors["invalid instanceof"].append((path, error_msg))
                else:
                    type_errors["other"].append((path, error_msg))

            elif "SyntaxError" in error_type:
                # Categorize syntax errors
                if "invalid redefinition" in error_msg:
                    syntax_errors["variable redefinition"].append((path, error_msg))
                elif "unexpected token" in error_msg:
                    syntax_errors["unexpected token"].append((path, error_msg))
                else:
                    syntax_errors["other"].append((path, error_msg))

        elif r["status"] == Status.COMPILE_FAIL:
            # Extract error type from compile error
            if ":" in error_msg:
                err_type = error_msg.split(":")[0].strip()
                compile_errors[err_type].append((path, error_msg))
            else:
                compile_errors["other"].append((path, error_msg))

        elif r["status"] == Status.RUNTIME_FAIL:
            expected = (r["cpython_output"] or "").strip()
            actual = (r["js_output"] or "").strip()
            output_mismatches.append((path, expected[:200], actual[:200]))

    # Generate HTML report
    html_content = generate_html_report(
        run=dict(run),
        by_status=by_status,
        reference_errors=reference_errors,
        type_errors=type_errors,
        syntax_errors=syntax_errors,
        compile_errors=compile_errors,
        output_mismatches=output_mismatches,
    )

    # Write report
    report_dir = DATA_DIR / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"run-{run_id:03d}.html"
    report_path.write_text(html_content)

    # Also write as latest.html
    latest_path = report_dir / "latest.html"
    latest_path.write_text(html_content)

    print(f"Report generated: {report_path}")
    print(f"Also available at: {latest_path}")


def generate_html_report(
    run: dict,
    by_status: dict,
    reference_errors: dict,
    type_errors: dict,
    syntax_errors: dict,
    compile_errors: dict,
    output_mismatches: list,
) -> str:
    """Generate the HTML report content."""
    import html

    total = run.get("total_programs", 0)
    passed = len(by_status.get(Status.RUNTIME_PASS, []))
    failed = len(by_status.get(Status.RUNTIME_FAIL, []))
    errors = len(by_status.get(Status.RUNTIME_ERROR, []))
    compile_fail = len(by_status.get(Status.COMPILE_FAIL, []))
    timeouts = len(by_status.get(Status.RUNTIME_TIMEOUT, [])) + len(
        by_status.get(Status.COMPILE_TIMEOUT, [])
    )

    pass_rate = (100 * passed / total) if total > 0 else 0

    # Sort reference errors by impact (most programs affected first)
    ref_errors_sorted = sorted(reference_errors.items(), key=lambda x: -len(x[1]))

    # Calculate potential impact of fixing each missing name
    total_ref_errors = sum(len(v) for v in reference_errors.values())

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prescrypt Test Report - Run #{run.get("id")}</title>
    <style>
        :root {{
            --pass-color: #22c55e;
            --fail-color: #ef4444;
            --warn-color: #f59e0b;
            --info-color: #3b82f6;
            --bg-color: #f8fafc;
            --card-bg: #ffffff;
            --text-color: #1e293b;
            --text-muted: #64748b;
            --border-color: #e2e8f0;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
            background: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
            padding: 2rem;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        h1 {{ font-size: 1.75rem; margin-bottom: 0.5rem; }}
        h2 {{ font-size: 1.25rem; margin: 1.5rem 0 1rem; color: var(--text-color); border-bottom: 2px solid var(--border-color); padding-bottom: 0.5rem; }}
        h3 {{ font-size: 1rem; margin: 1rem 0 0.5rem; color: var(--text-muted); }}
        .meta {{ color: var(--text-muted); font-size: 0.875rem; margin-bottom: 1.5rem; }}

        /* Dashboard */
        .dashboard {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .stat-card {{
            background: var(--card-bg);
            border-radius: 8px;
            padding: 1.25rem;
            border: 1px solid var(--border-color);
            text-align: center;
        }}
        .stat-value {{ font-size: 2rem; font-weight: 700; }}
        .stat-label {{ font-size: 0.75rem; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.05em; }}
        .stat-pass {{ color: var(--pass-color); }}
        .stat-fail {{ color: var(--fail-color); }}
        .stat-warn {{ color: var(--warn-color); }}

        /* Progress bar */
        .progress-container {{ margin-bottom: 2rem; }}
        .progress-bar {{
            height: 24px;
            background: var(--border-color);
            border-radius: 12px;
            overflow: hidden;
            display: flex;
        }}
        .progress-segment {{
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75rem;
            font-weight: 600;
            color: white;
            min-width: 30px;
        }}
        .segment-pass {{ background: var(--pass-color); }}
        .segment-fail {{ background: var(--fail-color); }}
        .segment-error {{ background: var(--warn-color); }}
        .segment-compile {{ background: #8b5cf6; }}

        /* Action items */
        .action-section {{
            background: var(--card-bg);
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid var(--border-color);
        }}
        .action-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }}
        .action-title {{ font-size: 1.1rem; font-weight: 600; }}
        .action-count {{
            background: var(--fail-color);
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.875rem;
            font-weight: 600;
        }}
        .action-description {{
            color: var(--text-muted);
            font-size: 0.875rem;
            margin-bottom: 1rem;
        }}

        /* Error tables */
        .error-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.875rem;
        }}
        .error-table th {{
            text-align: left;
            padding: 0.75rem;
            background: var(--bg-color);
            border-bottom: 2px solid var(--border-color);
            font-weight: 600;
        }}
        .error-table td {{
            padding: 0.75rem;
            border-bottom: 1px solid var(--border-color);
            vertical-align: top;
        }}
        .error-table tr:hover {{ background: var(--bg-color); }}
        .impact-high {{ color: var(--fail-color); font-weight: 600; }}
        .impact-medium {{ color: var(--warn-color); }}
        .impact-low {{ color: var(--text-muted); }}

        /* Code/path styling */
        code {{
            background: var(--bg-color);
            padding: 0.125rem 0.375rem;
            border-radius: 4px;
            font-size: 0.8125rem;
            font-family: 'SF Mono', Monaco, 'Courier New', monospace;
        }}
        .path-list {{
            font-size: 0.8125rem;
            color: var(--text-muted);
            max-height: 100px;
            overflow-y: auto;
        }}
        .path-list span {{ display: inline-block; margin-right: 0.5rem; }}

        /* Expandable sections */
        details {{
            margin-bottom: 0.5rem;
        }}
        summary {{
            cursor: pointer;
            padding: 0.5rem;
            background: var(--bg-color);
            border-radius: 4px;
            font-weight: 500;
        }}
        summary:hover {{ background: var(--border-color); }}
        .detail-content {{
            padding: 1rem;
            background: white;
            border: 1px solid var(--border-color);
            border-radius: 0 0 4px 4px;
            margin-top: -1px;
        }}

        /* Unified diff view */
        .diff-unified {{
            font-family: 'SF Mono', Monaco, 'Courier New', monospace;
            font-size: 0.8125rem;
            line-height: 1.5;
            background: #1e293b;
            color: #e2e8f0;
            padding: 1rem;
            border-radius: 6px;
            overflow-x: auto;
            max-height: 300px;
            overflow-y: auto;
            margin: 0;
        }}
        .diff-unified span {{
            display: block;
            padding: 0 0.5rem;
            margin: 0 -0.5rem;
        }}
        .diff-header {{
            color: #94a3b8;
            font-weight: 600;
        }}
        .diff-range {{
            color: #7dd3fc;
            background: rgba(56, 189, 248, 0.1);
        }}
        .diff-del {{
            background: rgba(248, 113, 113, 0.2);
            color: #fca5a5;
        }}
        .diff-add {{
            background: rgba(74, 222, 128, 0.2);
            color: #86efac;
        }}
        .diff-context {{
            color: #94a3b8;
        }}

        /* Priority badge */
        .priority {{
            display: inline-block;
            padding: 0.125rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        .priority-high {{ background: #fee2e2; color: #dc2626; }}
        .priority-medium {{ background: #fef3c7; color: #d97706; }}
        .priority-low {{ background: #e0e7ff; color: #4f46e5; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Prescrypt Test Report</h1>
        <div class="meta">
            Run #{run.get("id")} &bull;
            {run.get("git_branch", "unknown")} @ {run.get("git_commit", "unknown")[:8] if run.get("git_commit") else "unknown"} &bull;
            {run.get("started_at", "unknown")}
        </div>

        <!-- Dashboard -->
        <div class="dashboard">
            <div class="stat-card">
                <div class="stat-value">{total}</div>
                <div class="stat-label">Total Tests</div>
            </div>
            <div class="stat-card">
                <div class="stat-value stat-pass">{passed}</div>
                <div class="stat-label">Passing</div>
            </div>
            <div class="stat-card">
                <div class="stat-value stat-fail">{failed}</div>
                <div class="stat-label">Output Mismatch</div>
            </div>
            <div class="stat-card">
                <div class="stat-value stat-warn">{errors}</div>
                <div class="stat-label">Runtime Error</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: #8b5cf6;">{compile_fail}</div>
                <div class="stat-label">Compile Fail</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{pass_rate:.1f}%</div>
                <div class="stat-label">Pass Rate</div>
            </div>
        </div>

        <!-- Progress bar -->
        <div class="progress-container">
            <div class="progress-bar">
                <div class="progress-segment segment-pass" style="width: {100 * passed / total if total else 0:.1f}%">{passed}</div>
                <div class="progress-segment segment-fail" style="width: {100 * failed / total if total else 0:.1f}%">{failed}</div>
                <div class="progress-segment segment-error" style="width: {100 * errors / total if total else 0:.1f}%">{errors}</div>
                <div class="progress-segment segment-compile" style="width: {100 * compile_fail / total if total else 0:.1f}%">{compile_fail}</div>
            </div>
        </div>

        <!-- HIGH IMPACT: Missing Builtins/Names -->
        <h2>🎯 High-Impact Fixes: Missing Names</h2>
        <p class="action-description">
            These undefined names cause the most test failures. Implementing them would fix multiple tests at once.
        </p>
        <div class="action-section">
            <table class="error-table">
                <thead>
                    <tr>
                        <th>Priority</th>
                        <th>Missing Name</th>
                        <th>Tests Affected</th>
                        <th>Impact</th>
                        <th>Example Programs</th>
                    </tr>
                </thead>
                <tbody>
                    {generate_missing_names_rows(ref_errors_sorted, total_ref_errors)}
                </tbody>
            </table>
        </div>

        <!-- Compile Errors -->
        <h2>🔧 Compilation Errors</h2>
        <p class="action-description">
            These programs fail during Python-to-JS compilation. Often indicates unsupported syntax or features.
        </p>
        {generate_compile_errors_section(compile_errors)}

        <!-- Type Errors -->
        <h2>⚠️ Type Errors at Runtime</h2>
        <p class="action-description">
            JavaScript runtime type errors, often from incorrect method calls or missing prototypes.
        </p>
        {generate_type_errors_section(type_errors)}

        <!-- Syntax Errors -->
        <h2>📝 JavaScript Syntax Errors</h2>
        <p class="action-description">
            Generated JavaScript has syntax issues. Usually indicates code generation bugs.
        </p>
        {generate_syntax_errors_section(syntax_errors)}

        <!-- Output Mismatches -->
        <h2>📊 Output Mismatches ({len(output_mismatches)} tests)</h2>
        <p class="action-description">
            These tests compile and run, but produce different output than Python. Often the hardest to fix.
        </p>
        {generate_output_mismatch_section(output_mismatches[:50])}

    </div>
</body>
</html>
"""


def generate_missing_names_rows(ref_errors_sorted: list, total: int) -> str:
    """Generate table rows for missing names."""
    import html

    rows = []
    for name, paths in ref_errors_sorted[:20]:
        if name == "_other_":
            continue
        count = len(paths)
        impact_pct = 100 * count / total if total else 0

        if count >= 10:
            priority = '<span class="priority priority-high">HIGH</span>'
            impact_class = "impact-high"
        elif count >= 5:
            priority = '<span class="priority priority-medium">MEDIUM</span>'
            impact_class = "impact-medium"
        else:
            priority = '<span class="priority priority-low">LOW</span>'
            impact_class = "impact-low"

        examples = ", ".join(
            f"<code>{html.escape(p.split('/')[-1])}</code>" for p in paths[:3]
        )
        if len(paths) > 3:
            examples += f" +{len(paths) - 3} more"

        rows.append(f"""
            <tr>
                <td>{priority}</td>
                <td><code>{html.escape(name)}</code></td>
                <td class="{impact_class}">{count}</td>
                <td class="{impact_class}">{impact_pct:.1f}%</td>
                <td>{examples}</td>
            </tr>
        """)
    return "\n".join(rows)


def generate_compile_errors_section(compile_errors: dict) -> str:
    """Generate section for compile errors."""
    import html

    if not compile_errors:
        return '<div class="action-section"><p>No compilation errors! 🎉</p></div>'

    sections = []
    for error_type, items in sorted(compile_errors.items(), key=lambda x: -len(x[1])):
        count = len(items)
        examples_html = []
        for path, msg in items[:5]:
            short_msg = msg[:100] + "..." if len(msg) > 100 else msg
            examples_html.append(
                f"<li><code>{html.escape(path.split('/')[-1])}</code>: {html.escape(short_msg)}</li>"
            )

        if len(items) > 5:
            examples_html.append(f"<li><em>...and {len(items) - 5} more</em></li>")

        sections.append(f"""
        <details>
            <summary><strong>{html.escape(error_type)}</strong> ({count} programs)</summary>
            <div class="detail-content">
                <ul>{"".join(examples_html)}</ul>
            </div>
        </details>
        """)

    return f'<div class="action-section">{chr(10).join(sections)}</div>'


def generate_type_errors_section(type_errors: dict) -> str:
    """Generate section for type errors."""
    import html

    if not type_errors:
        return '<div class="action-section"><p>No type errors! 🎉</p></div>'

    sections = []
    for error_type, items in sorted(type_errors.items(), key=lambda x: -len(x[1])):
        count = len(items)
        examples_html = []
        for path, msg in items[:5]:
            short_msg = msg[:80] + "..." if len(msg) > 80 else msg
            examples_html.append(
                f"<li><code>{html.escape(path.split('/')[-1])}</code>: {html.escape(short_msg)}</li>"
            )

        if len(items) > 5:
            examples_html.append(f"<li><em>...and {len(items) - 5} more</em></li>")

        sections.append(f"""
        <details>
            <summary><strong>{html.escape(error_type)}</strong> ({count} programs)</summary>
            <div class="detail-content">
                <ul>{"".join(examples_html)}</ul>
            </div>
        </details>
        """)

    return f'<div class="action-section">{chr(10).join(sections)}</div>'


def generate_syntax_errors_section(syntax_errors: dict) -> str:
    """Generate section for syntax errors."""
    import html

    if not syntax_errors:
        return '<div class="action-section"><p>No syntax errors! 🎉</p></div>'

    sections = []
    for error_type, items in sorted(syntax_errors.items(), key=lambda x: -len(x[1])):
        count = len(items)
        examples_html = []
        for path, msg in items[:5]:
            short_msg = msg[:80] + "..." if len(msg) > 80 else msg
            examples_html.append(
                f"<li><code>{html.escape(path.split('/')[-1])}</code>: {html.escape(short_msg)}</li>"
            )

        sections.append(f"""
        <details>
            <summary><strong>{html.escape(error_type)}</strong> ({count} programs)</summary>
            <div class="detail-content">
                <ul>{"".join(examples_html)}</ul>
            </div>
        </details>
        """)

    return f'<div class="action-section">{chr(10).join(sections)}</div>'


def generate_unified_diff(expected: str, actual: str) -> str:
    """Generate a unified diff HTML representation."""
    import difflib
    import html as html_module

    expected_lines = expected.splitlines(keepends=True)
    actual_lines = actual.splitlines(keepends=True)

    # Use difflib to get the differences
    diff = list(
        difflib.unified_diff(
            expected_lines,
            actual_lines,
            fromfile="expected (Python)",
            tofile="actual (JavaScript)",
            lineterm="",
        )
    )

    if not diff:
        # No differences (shouldn't happen, but handle it)
        return f'<pre class="diff-unified">{html_module.escape(expected)}</pre>'

    lines_html = []
    for line in diff:
        escaped = html_module.escape(line.rstrip("\n"))
        if line.startswith("+++") or line.startswith("---"):
            lines_html.append(f'<span class="diff-header">{escaped}</span>')
        elif line.startswith("@@"):
            lines_html.append(f'<span class="diff-range">{escaped}</span>')
        elif line.startswith("-"):
            lines_html.append(f'<span class="diff-del">{escaped}</span>')
        elif line.startswith("+"):
            lines_html.append(f'<span class="diff-add">{escaped}</span>')
        else:
            lines_html.append(f'<span class="diff-context">{escaped}</span>')

    return '<pre class="diff-unified">' + "\n".join(lines_html) + "</pre>"


def generate_output_mismatch_section(mismatches: list) -> str:
    """Generate section for output mismatches."""
    import html

    if not mismatches:
        return '<div class="action-section"><p>No output mismatches! 🎉</p></div>'

    items = []
    for path, expected, actual in mismatches[:30]:
        filename = path.split("/")[-1]
        diff_html = generate_unified_diff(expected, actual)
        items.append(f"""
        <details>
            <summary><code>{html.escape(filename)}</code></summary>
            <div class="detail-content">
                {diff_html}
            </div>
        </details>
        """)

    return f'<div class="action-section">{chr(10).join(items)}</div>'


def cmd_classify(args, config: Config, db: TestDatabase):
    """Run full classification pipeline: discover -> validate -> run."""
    print("Running full classification pipeline...")
    print()

    # Step 1: Discover
    print("Step 1: Discovering programs...")
    cmd_discover(args, config, db)
    print()

    # Step 2: Validate on CPython
    print("Step 2: Validating on CPython...")

    # Create a mock args object with the right attributes
    class MockArgs:
        verbose = args.verbose
        only_new = True
        only_failed = False
        filter = None

    cmd_validate_cpython(MockArgs(), config, db)
    print()

    # Step 3: Run tests
    print("Step 3: Running tests...")

    class MockRunArgs:
        verbose = args.verbose
        filter = None
        only_failed = False
        all = False

    cmd_run(MockRunArgs(), config, db)


def main():
    parser = argparse.ArgumentParser(
        description="Prescrypt Test Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--config", type=Path, help="Path to config file")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # discover
    discover_parser = subparsers.add_parser("discover", help="Find all test programs")

    # validate-cpython
    validate_parser = subparsers.add_parser(
        "validate-cpython", help="Validate programs on CPython"
    )
    validate_parser.add_argument(
        "--only-new", action="store_true", help="Only validate new programs"
    )
    validate_parser.add_argument(
        "--only-failed", action="store_true", help="Only re-validate failed programs"
    )
    validate_parser.add_argument(
        "--filter", type=str, help="Filter programs by glob pattern"
    )

    # status
    status_parser = subparsers.add_parser("status", help="Show current status")

    # import-denylist
    import_parser = subparsers.add_parser(
        "import-denylist", help="Import from existing denylist.py"
    )

    # run
    run_parser = subparsers.add_parser("run", help="Run tests through full pipeline")
    run_parser.add_argument(
        "--filter", type=str, help="Filter programs by glob pattern"
    )
    run_parser.add_argument(
        "--only-failed", action="store_true", help="Only re-run previously failed tests"
    )
    run_parser.add_argument(
        "--all", action="store_true", help="Run all programs (not just CPython PASS)"
    )

    # classify
    classify_parser = subparsers.add_parser(
        "classify", help="Full classification pipeline (discover + validate + run)"
    )

    # report
    report_parser = subparsers.add_parser("report", help="Generate HTML report")
    report_parser.add_argument(
        "--run", type=int, help="Run ID to report on (default: latest)"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Load config
    config = Config.load(args.config)

    # Open database
    db = TestDatabase()

    try:
        if args.command == "discover":
            cmd_discover(args, config, db)
        elif args.command == "validate-cpython":
            cmd_validate_cpython(args, config, db)
        elif args.command == "status":
            cmd_status(args, config, db)
        elif args.command == "import-denylist":
            cmd_import_denylist(args, config, db)
        elif args.command == "run":
            cmd_run(args, config, db)
        elif args.command == "classify":
            cmd_classify(args, config, db)
        elif args.command == "report":
            cmd_report(args, config, db)
        else:
            print(f"Unknown command: {args.command}")
            return 1
    finally:
        db.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
