#!/usr/bin/env python3
"""Test Manager for Prescrypt end-to-end tests.

This script is a thin CLI wrapper around the prescrypt.testing module.

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
import sys
from pathlib import Path

from prescrypt.testing import Config, ResultsDatabase
from prescrypt.testing.cli import (
    cmd_classify,
    cmd_discover,
    cmd_export_denylist,
    cmd_import_denylist,
    cmd_report,
    cmd_run,
    cmd_status,
    cmd_validate_cpython,
)


def main():
    parser = argparse.ArgumentParser(
        description="Prescrypt Test Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--config", type=Path, help="Path to config file")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # discover
    subparsers.add_parser("discover", help="Find all test programs")

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
    subparsers.add_parser("status", help="Show current status")

    # import-denylist
    subparsers.add_parser(
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
    subparsers.add_parser(
        "classify", help="Full classification pipeline (discover + validate + run)"
    )

    # export-denylist
    export_parser = subparsers.add_parser(
        "export-denylist", help="Export failing tests to known_failures in test-config.toml"
    )
    export_parser.add_argument(
        "--run", type=int, help="Run ID to export from (default: latest)"
    )
    export_parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be updated without writing"
    )

    # report
    report_parser = subparsers.add_parser("report", help="Generate test report")
    report_parser.add_argument(
        "--run", type=int, help="Run ID to report on (default: latest)"
    )
    report_parser.add_argument(
        "--format",
        choices=["html", "markdown", "both"],
        default="html",
        help="Output format (default: html)",
    )
    report_parser.add_argument(
        "--filter",
        type=str,
        help="Regex pattern to filter errors (e.g., 'Base classes')",
    )
    report_parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output file path (for markdown, prints to stdout if not specified)",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Load config
    config = Config.load(args.config)

    # Open database
    db = ResultsDatabase()

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
        elif args.command == "export-denylist":
            cmd_export_denylist(args, config, db)
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
