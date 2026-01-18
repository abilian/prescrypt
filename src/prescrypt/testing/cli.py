"""CLI commands for the test manager.

This module provides all the command implementations for the test manager.
"""

from __future__ import annotations

import ast
from collections import defaultdict
from pathlib import Path

from .database import ResultsDatabase
from .discovery import discover_programs, validate_cpython
from .models import Config, Program, Status
from .paths import DATA_DIR, PROGRAMS_DIR, PROJECT_ROOT
from .reports import categorize_results, generate_html_report, generate_markdown_report
from .runner import run_program_test


def cmd_discover(args, config: Config, db: ResultsDatabase):
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
    for source, cnt in sorted(sources.items()):
        print(f"  {source}: {cnt}")


def cmd_validate_cpython(args, config: Config, db: ResultsDatabase):
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
                "+"
                if status == Status.CPYTHON_PASS
                else "x"
                if status == Status.CPYTHON_FAIL
                else "o"
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


def cmd_status(args, config: Config, db: ResultsDatabase):
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


def cmd_import_denylist(args, config: Config, db: ResultsDatabase):
    """Import programs from existing denylist files."""
    denylist_path = (
        PROJECT_ROOT / "tests" / "c_e2e" / "from_micropython" / "denylist.py"
    )

    if not denylist_path.exists():
        print(f"Denylist not found: {denylist_path}")
        return

    # Parse the denylist.py file
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


def cmd_run(args, config: Config, db: ResultsDatabase):
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

        results = run_program_test(program, config)

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


def cmd_report(args, config: Config, db: ResultsDatabase):
    """Generate HTML report for test results."""
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
    reference_errors, type_errors, syntax_errors, compile_errors, output_mismatches = (
        categorize_results(results)
    )

    # Get format and filter options
    output_format = getattr(args, "format", "html")
    filter_pattern = getattr(args, "filter", None)
    output_path = getattr(args, "output", None)

    report_dir = DATA_DIR / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    # Generate HTML report
    if output_format in ("html", "both"):
        html_content = generate_html_report(
            run=dict(run),
            by_status=by_status,
            reference_errors=reference_errors,
            type_errors=type_errors,
            syntax_errors=syntax_errors,
            compile_errors=compile_errors,
            output_mismatches=output_mismatches,
        )

        report_path = report_dir / f"run-{run_id:03d}.html"
        report_path.write_text(html_content)

        # Also write as latest.html
        latest_path = report_dir / "latest.html"
        latest_path.write_text(html_content)

        print(f"HTML report: {report_path}")
        print(f"Also available at: {latest_path}")

    # Generate Markdown report
    if output_format in ("markdown", "both"):
        md_content = generate_markdown_report(
            run=dict(run),
            by_status=by_status,
            reference_errors=reference_errors,
            type_errors=type_errors,
            syntax_errors=syntax_errors,
            compile_errors=compile_errors,
            output_mismatches=output_mismatches,
            filter_pattern=filter_pattern,
        )

        if output_path:
            # Write to specified file
            Path(output_path).write_text(md_content)
            print(f"Markdown report: {output_path}")
        elif output_format == "markdown":
            # Print to stdout if markdown-only and no output file
            print(md_content)
        else:
            # Write to default location for "both" format
            md_path = report_dir / f"run-{run_id:03d}.md"
            md_path.write_text(md_content)
            print(f"Markdown report: {md_path}")


def cmd_classify(args, config: Config, db: ResultsDatabase):
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


def cmd_export_denylist(args, config: Config, db: ResultsDatabase):
    """Export failing tests to known_failures in test-config.toml."""
    import tomlkit

    from .paths import CONFIG_PATH

    run_id = args.run if hasattr(args, "run") and args.run else None

    if run_id is None:
        # Get latest run
        latest = db.get_latest_run()
        if not latest:
            print("No test runs found. Run 'test_manager.py run' first.")
            return
        run_id = latest["id"]

    # Get all failing results for this run
    # We use 'node' runtime as the reference (same as reports)
    failing_statuses = [
        Status.COMPILE_FAIL,
        Status.COMPILE_TIMEOUT,
        Status.RUNTIME_ERROR,
        Status.RUNTIME_FAIL,
        Status.RUNTIME_TIMEOUT,
    ]
    placeholders = ",".join("?" * len(failing_statuses))

    cursor = db.conn.execute(
        f"""
        SELECT DISTINCT p.path
        FROM results r
        JOIN programs p ON r.program_id = p.id
        WHERE r.run_id = ? AND r.runtime = 'node' AND r.status IN ({placeholders})
        ORDER BY p.path
        """,
        (run_id, *failing_statuses),
    )

    failing_paths = [row[0] for row in cursor.fetchall()]

    if not failing_paths:
        print(f"No failing tests found in run #{run_id}")
        return

    print(f"Found {len(failing_paths)} failing tests in run #{run_id}")

    # Load the existing config file
    if not CONFIG_PATH.exists():
        print(f"Config file not found: {CONFIG_PATH}")
        return

    with open(CONFIG_PATH) as f:
        doc = tomlkit.load(f)

    # Update known_failures
    if "manual_overrides" not in doc:
        doc["manual_overrides"] = tomlkit.table()

    # Get current known_failures to show diff
    current_failures = set(doc["manual_overrides"].get("known_failures", []))
    new_failures = set(failing_paths)

    added = new_failures - current_failures
    removed = current_failures - new_failures

    # Update the list
    doc["manual_overrides"]["known_failures"] = sorted(failing_paths)

    # Write back
    if args.dry_run:
        print("\nDry run - would update known_failures to:")
        for path in sorted(failing_paths)[:20]:
            print(f"  - {path}")
        if len(failing_paths) > 20:
            print(f"  ... and {len(failing_paths) - 20} more")

        if added:
            print(f"\nWould add {len(added)} new failures")
        if removed:
            print(f"Would remove {len(removed)} previously known failures (now passing)")
    else:
        with open(CONFIG_PATH, "w") as f:
            tomlkit.dump(doc, f)

        print(f"\nUpdated {CONFIG_PATH}")
        print(f"  Total known failures: {len(failing_paths)}")

        if added:
            print(f"  Added: {len(added)} new failures")
            if args.verbose:
                for path in sorted(added)[:10]:
                    print(f"    + {path}")
                if len(added) > 10:
                    print(f"    ... and {len(added) - 10} more")

        if removed:
            print(f"  Removed: {len(removed)} now-passing tests")
            if args.verbose:
                for path in sorted(removed)[:10]:
                    print(f"    - {path}")
                if len(removed) > 10:
                    print(f"    ... and {len(removed) - 10} more")
