#!/usr/bin/env python3
"""Coverage report with context for uncovered lines.

Reads .coverage file and shows uncovered lines with surrounding context,
including class and function names.

Usage:
    python scripts/coverage_report.py [--context N] [--min-miss N] [pattern]

Options:
    --context N    Lines of context around uncovered code (default: 2)
    --min-miss N   Only show files with at least N missed lines (default: 1)
    pattern        Filter files by pattern (e.g., "codegen" or "stdlib_py")

Examples:
    python scripts/coverage_report.py                    # All files with missing coverage
    python scripts/coverage_report.py codegen            # Only codegen/* files
    python scripts/coverage_report.py stdlib_py -m 5     # stdlib_py with 5+ missing
    python scripts/coverage_report.py -c 3 expressions   # More context
"""
from __future__ import annotations

import argparse
import ast
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    from coverage import Coverage
except ImportError:
    print("Error: coverage package not installed. Run: pip install coverage")
    sys.exit(1)


# ANSI colors
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


def use_colors() -> bool:
    """Check if we should use colors (stdout is a TTY)."""
    return sys.stdout.isatty()


@dataclass
class ScopeInfo:
    """Information about a class or function scope."""

    name: str
    type: str  # "class" or "function"
    start_line: int
    end_line: int
    parent: str | None = None

    def full_name(self) -> str:
        if self.parent:
            return f"{self.parent}.{self.name}"
        return self.name


def get_scopes(source: str) -> list[ScopeInfo]:
    """Parse source and return all class/function scopes."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    scopes = []

    def visit(node, parent_name=None):
        if isinstance(node, ast.ClassDef):
            scope = ScopeInfo(
                name=node.name,
                type="class",
                start_line=node.lineno,
                end_line=node.end_lineno or node.lineno,
                parent=parent_name,
            )
            scopes.append(scope)
            for child in ast.iter_child_nodes(node):
                visit(child, node.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            scope = ScopeInfo(
                name=node.name,
                type="function",
                start_line=node.lineno,
                end_line=node.end_lineno or node.lineno,
                parent=parent_name,
            )
            scopes.append(scope)
            for child in ast.iter_child_nodes(node):
                visit(child, f"{parent_name}.{node.name}" if parent_name else node.name)
        else:
            for child in ast.iter_child_nodes(node):
                visit(child, parent_name)

    for node in ast.iter_child_nodes(tree):
        visit(node)

    return scopes


def find_scope_for_line(scopes: list[ScopeInfo], line: int) -> ScopeInfo | None:
    """Find the innermost scope containing the given line."""
    matching = [s for s in scopes if s.start_line <= line <= s.end_line]
    if not matching:
        return None
    # Return the innermost (smallest range)
    return min(matching, key=lambda s: s.end_line - s.start_line)


def group_lines_with_gap(lines: list[int], gap: int = 5) -> list[tuple[int, int]]:
    """Group line numbers that are close together (within gap lines)."""
    if not lines:
        return []

    lines = sorted(lines)
    groups = []
    start = lines[0]
    end = lines[0]

    for line in lines[1:]:
        if line <= end + gap:
            end = line
        else:
            groups.append((start, end))
            start = line
            end = line

    groups.append((start, end))
    return groups


def format_file_report(
    filepath: str,
    source_lines: list[str],
    missing_lines: set[int],
    scopes: list[ScopeInfo],
    context: int = 2,
    colors: bool = True,
) -> str:
    """Format a report for a single file with context."""
    output = []
    c = Colors if colors else type("NoColors", (), {k: "" for k in dir(Colors) if not k.startswith("_")})()

    # Group lines that are close together (within context * 2 + 1 lines)
    groups = group_lines_with_gap(sorted(missing_lines), gap=context * 2 + 1)

    for start, end in groups:
        # Find the scope for the start of this group
        scope = find_scope_for_line(scopes, start)

        # Build header showing scope
        if scope:
            scope_type = "class" if scope.type == "class" else "def"
            header = f"{c.CYAN}  # In {scope.full_name()}() [{scope_type}]{c.RESET}"
        else:
            header = f"{c.CYAN}  # At module level{c.RESET}"

        output.append(header)

        # Calculate display range with context
        display_start = max(1, start - context)
        display_end = min(len(source_lines), end + context)

        # If scope exists and definition is close, include it
        if scope and scope.start_line >= display_start - 3:
            display_start = scope.start_line

        # Show ellipsis if we're not starting from line 1
        if display_start > 1:
            output.append(f"{c.DIM}  ...{c.RESET}")

        # Show lines with markers
        for line_num in range(display_start, display_end + 1):
            if line_num <= len(source_lines):
                line_content = source_lines[line_num - 1].rstrip()

                # Truncate long lines
                max_len = 72
                if len(line_content) > max_len:
                    line_content = line_content[: max_len - 3] + "..."

                if line_num in missing_lines:
                    marker = f"{c.RED}>{c.RESET}"
                    line_text = f"{c.RED}{line_content}{c.RESET}"
                    suffix = f"  {c.YELLOW}# NOT COVERED{c.RESET}"
                else:
                    marker = " "
                    line_text = f"{c.DIM}{line_content}{c.RESET}"
                    suffix = ""

                output.append(f"  {marker} {line_num:4d} | {line_text}{suffix}")

        # Show ellipsis if we're not at the end
        if display_end < len(source_lines):
            output.append(f"{c.DIM}  ...{c.RESET}")

        output.append("")  # Blank line between groups

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Coverage report with context for uncovered lines",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/coverage_report.py                    # All files
    python scripts/coverage_report.py codegen            # Only codegen/* files
    python scripts/coverage_report.py stdlib_py -m 5     # 5+ missing lines
    python scripts/coverage_report.py -c 3 expressions   # More context
        """,
    )
    parser.add_argument(
        "--context",
        "-c",
        type=int,
        default=2,
        help="Lines of context around uncovered code (default: 2)",
    )
    parser.add_argument(
        "--min-miss",
        "-m",
        type=int,
        default=1,
        help="Only show files with at least N missed lines (default: 1)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )
    parser.add_argument(
        "pattern",
        nargs="?",
        default="",
        help="Filter files by pattern (e.g., 'codegen' or 'stdlib_py')",
    )
    args = parser.parse_args()

    colors = use_colors() and not args.no_color
    c = Colors if colors else type("NoColors", (), {k: "" for k in dir(Colors) if not k.startswith("_")})()

    # Load coverage data
    cov = Coverage()
    try:
        cov.load()
    except Exception as e:
        print(f"Error loading .coverage file: {e}")
        print("Run 'pytest --cov' first to generate coverage data.")
        sys.exit(1)

    # Get coverage data
    data = cov.get_data()
    measured_files = data.measured_files()

    # Filter and sort files
    if args.pattern:
        measured_files = [f for f in measured_files if args.pattern in f]

    measured_files = sorted(measured_files)

    # Summary stats
    total_statements = 0
    total_missing = 0
    files_with_missing = 0

    print(f"{c.BOLD}{'=' * 80}{c.RESET}")
    print(f"{c.BOLD}COVERAGE REPORT WITH CONTEXT{c.RESET}")
    print(f"{c.BOLD}{'=' * 80}{c.RESET}")
    print()

    for filepath in measured_files:
        try:
            path = Path(filepath)
            if not path.exists():
                continue

            source = path.read_text()
            source_lines = source.splitlines()

            # Get analysis for this file
            analysis = cov.analysis2(filepath)
            # analysis returns: (filename, executable, excluded, missing, formatted_missing)
            _, executable, _, missing, _ = analysis

            if len(missing) < args.min_miss:
                continue

            total_statements += len(executable)
            total_missing += len(missing)
            files_with_missing += 1

            # Parse scopes
            scopes = get_scopes(source)

            # Calculate coverage percentage
            if executable:
                cover_pct = 100 * (len(executable) - len(missing)) / len(executable)
            else:
                cover_pct = 100

            # Color code the percentage
            if cover_pct >= 80:
                pct_color = c.GREEN
            elif cover_pct >= 60:
                pct_color = c.YELLOW
            else:
                pct_color = c.RED

            # Print file header
            rel_path = filepath
            if "src/prescrypt" in filepath:
                rel_path = filepath.split("src/prescrypt/")[1]

            print(f"{c.BOLD}{'-' * 80}{c.RESET}")
            print(f"{c.BOLD}FILE: {c.BLUE}{rel_path}{c.RESET}")
            print(
                f"      Stmts: {len(executable)}, "
                f"Missing: {c.RED}{len(missing)}{c.RESET}, "
                f"Coverage: {pct_color}{cover_pct:.0f}%{c.RESET}"
            )
            print(f"{c.BOLD}{'-' * 80}{c.RESET}")

            # Print context for missing lines
            report = format_file_report(
                filepath, source_lines, set(missing), scopes, args.context, colors
            )
            print(report)

        except Exception as e:
            print(f"Error processing {filepath}: {e}")
            continue

    # Print summary
    print(f"{c.BOLD}{'=' * 80}{c.RESET}")
    print(f"{c.BOLD}SUMMARY{c.RESET}")
    print(f"{c.BOLD}{'=' * 80}{c.RESET}")
    print(f"Files with missing coverage: {files_with_missing}")
    print(f"Total statements: {total_statements}")
    print(f"Total missing: {c.RED}{total_missing}{c.RESET}")
    if total_statements:
        overall = 100 * (total_statements - total_missing) / total_statements
        if overall >= 80:
            pct_color = c.GREEN
        elif overall >= 60:
            pct_color = c.YELLOW
        else:
            pct_color = c.RED
        print(f"Overall coverage: {pct_color}{overall:.1f}%{c.RESET}")
    print()


if __name__ == "__main__":
    main()
