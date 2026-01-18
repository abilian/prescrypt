from __future__ import annotations

# Expression testing utilities (original)
from .data import EXPRESSIONS

# Test manager database
from .database import ResultsDatabase

# Discovery and validation
from .discovery import discover_programs, validate_cpython

# Test manager models
from .models import Config, Program, Status, TestResult

# Project paths
from .paths import (
    CONFIG_PATH,
    DATA_DIR,
    DATABASE_PATH,
    PROGRAMS_DIR,
    PROJECT_ROOT,
)

# Report generation
from .reports import (
    categorize_results,
    generate_html_report,
    generate_markdown_report,
)

# Compilation and execution
from .runner import compile_program, run_javascript, run_program_test
from .utils import js_eq, js_eval

__all__ = [
    # Original expression testing
    "EXPRESSIONS",
    "js_eval",
    "js_eq",
    # Models
    "Config",
    "Program",
    "Status",
    "TestResult",
    # Database
    "ResultsDatabase",
    # Paths
    "CONFIG_PATH",
    "DATA_DIR",
    "DATABASE_PATH",
    "PROGRAMS_DIR",
    "PROJECT_ROOT",
    # Discovery
    "discover_programs",
    "validate_cpython",
    # Runner
    "compile_program",
    "run_javascript",
    "run_program_test",
    # Reports
    "categorize_results",
    "generate_html_report",
    "generate_markdown_report",
]
