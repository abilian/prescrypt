"""SQLite database for storing test results.

This module provides the ResultsDatabase class that manages all database
operations for the test manager.
"""

from __future__ import annotations

import hashlib
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from .models import Program, TestResult
from .paths import DATABASE_PATH, PROJECT_ROOT


class ResultsDatabase:
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
        # Safe: placeholders are just "?" characters, not user input
        query = f"SELECT * FROM programs WHERE cpython_status IN ({placeholders})"  # noqa: S608
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
        return cursor.lastrowid or 0

    def update_cpython_status(
        self,
        path: str,
        status: str,
        output: str | None = None,
        error: str | None = None,
    ):
        """Update CPython validation status for a program."""
        output_hash = (
            hashlib.md5(output.encode(), usedforsecurity=False).hexdigest()
            if output
            else None
        )
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
            (
                datetime.now(tz=timezone.utc),
                git_commit,
                git_branch,
                python_version,
                notes,
            ),
        )
        self.conn.commit()
        return cursor.lastrowid or 0

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
            (
                datetime.now(tz=timezone.utc),
                total,
                passed,
                failed,
                skipped,
                errors,
                run_id,
            ),
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
                check=False,
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
                check=False,
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
