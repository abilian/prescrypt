"""Report generation for test results.

This module provides functions to generate HTML and Markdown reports
from test results.
"""

from __future__ import annotations

import difflib
import html
import re
from collections import defaultdict

from .models import Status


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

        /* Error item details */
        .error-item {{
            margin: 0.25rem 0;
        }}
        .error-item summary {{
            padding: 0.375rem 0.5rem;
            font-size: 0.8125rem;
        }}
        .error-details {{
            padding: 0.75rem;
            background: var(--bg-color);
            border-radius: 0 0 4px 4px;
        }}
        .error-message {{
            font-family: 'SF Mono', Monaco, 'Courier New', monospace;
            font-size: 0.75rem;
            background: #1e293b;
            color: #e2e8f0;
            padding: 0.75rem;
            border-radius: 4px;
            overflow-x: auto;
            white-space: pre-wrap;
            word-break: break-word;
            margin: 0;
        }}
        .path-list {{
            max-height: 400px;
            overflow-y: auto;
            padding: 0.5rem;
            background: var(--bg-color);
            border-radius: 4px;
            font-size: 0.8125rem;
            line-height: 1.8;
        }}
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
        <h2>High-Impact Fixes: Missing Names</h2>
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
                    {_generate_missing_names_rows(ref_errors_sorted, total_ref_errors)}
                </tbody>
            </table>
        </div>

        <!-- Compile Errors -->
        <h2>Compilation Errors</h2>
        <p class="action-description">
            These programs fail during Python-to-JS compilation. Often indicates unsupported syntax or features.
        </p>
        {_generate_compile_errors_section(compile_errors)}

        <!-- Type Errors -->
        <h2>Type Errors at Runtime</h2>
        <p class="action-description">
            JavaScript runtime type errors, often from incorrect method calls or missing prototypes.
        </p>
        {_generate_type_errors_section(type_errors)}

        <!-- Syntax Errors -->
        <h2>JavaScript Syntax Errors</h2>
        <p class="action-description">
            Generated JavaScript has syntax issues. Usually indicates code generation bugs.
        </p>
        {_generate_syntax_errors_section(syntax_errors)}

        <!-- Output Mismatches -->
        <h2>Output Mismatches ({len(output_mismatches)} tests)</h2>
        <p class="action-description">
            These tests compile and run, but produce different output than Python. Often the hardest to fix.
        </p>
        {_generate_output_mismatch_section(output_mismatches)}

    </div>
</body>
</html>
"""


def _generate_missing_names_rows(ref_errors_sorted: list, total: int) -> str:
    """Generate table rows for missing names."""
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

        # Show all affected programs in an expandable list
        all_paths = "<br>".join(
            f"<code>programs/{html.escape(p)}</code>" for p in sorted(paths)
        )

        rows.append(f"""
            <tr>
                <td>{priority}</td>
                <td><code>{html.escape(name)}</code></td>
                <td class="{impact_class}">{count}</td>
                <td class="{impact_class}">{impact_pct:.1f}%</td>
                <td>
                    <details>
                        <summary>Show {count} affected programs</summary>
                        <div class="path-list">{all_paths}</div>
                    </details>
                </td>
            </tr>
        """)
    return "\n".join(rows)


def _generate_compile_errors_section(compile_errors: dict) -> str:
    """Generate section for compile errors."""
    if not compile_errors:
        return '<div class="action-section"><p>No compilation errors!</p></div>'

    sections = []
    for error_type, items in sorted(compile_errors.items(), key=lambda x: -len(x[1])):
        count = len(items)
        # Show ALL items with full details
        items_html = []
        for path, msg in sorted(items, key=lambda x: x[0]):
            full_path = f"programs/{path}"
            items_html.append(f"""
                <details class="error-item">
                    <summary><code>{html.escape(full_path)}</code></summary>
                    <div class="error-details">
                        <pre class="error-message">{html.escape(msg)}</pre>
                    </div>
                </details>
            """)

        sections.append(f"""
        <details>
            <summary><strong>{html.escape(error_type)}</strong> ({count} programs)</summary>
            <div class="detail-content">
                {"".join(items_html)}
            </div>
        </details>
        """)

    return f'<div class="action-section">{chr(10).join(sections)}</div>'


def _generate_type_errors_section(type_errors: dict) -> str:
    """Generate section for type errors."""
    if not type_errors:
        return '<div class="action-section"><p>No type errors!</p></div>'

    sections = []
    for error_type, items in sorted(type_errors.items(), key=lambda x: -len(x[1])):
        count = len(items)
        # Show ALL items with full details
        items_html = []
        for path, msg in sorted(items, key=lambda x: x[0]):
            full_path = f"programs/{path}"
            items_html.append(f"""
                <details class="error-item">
                    <summary><code>{html.escape(full_path)}</code></summary>
                    <div class="error-details">
                        <pre class="error-message">{html.escape(msg)}</pre>
                    </div>
                </details>
            """)

        sections.append(f"""
        <details>
            <summary><strong>{html.escape(error_type)}</strong> ({count} programs)</summary>
            <div class="detail-content">
                {"".join(items_html)}
            </div>
        </details>
        """)

    return f'<div class="action-section">{chr(10).join(sections)}</div>'


def _generate_syntax_errors_section(syntax_errors: dict) -> str:
    """Generate section for syntax errors."""
    if not syntax_errors:
        return '<div class="action-section"><p>No syntax errors!</p></div>'

    sections = []
    for error_type, items in sorted(syntax_errors.items(), key=lambda x: -len(x[1])):
        count = len(items)
        # Show ALL items with full details
        items_html = []
        for path, msg in sorted(items, key=lambda x: x[0]):
            full_path = f"programs/{path}"
            items_html.append(f"""
                <details class="error-item">
                    <summary><code>{html.escape(full_path)}</code></summary>
                    <div class="error-details">
                        <pre class="error-message">{html.escape(msg)}</pre>
                    </div>
                </details>
            """)

        sections.append(f"""
        <details>
            <summary><strong>{html.escape(error_type)}</strong> ({count} programs)</summary>
            <div class="detail-content">
                {"".join(items_html)}
            </div>
        </details>
        """)

    return f'<div class="action-section">{chr(10).join(sections)}</div>'


def _generate_unified_diff(expected: str, actual: str) -> str:
    """Generate a unified diff HTML representation."""
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
        return f'<pre class="diff-unified">{html.escape(expected)}</pre>'

    lines_html = []
    for line in diff:
        escaped = html.escape(line.rstrip("\n"))
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


def _generate_output_mismatch_section(mismatches: list) -> str:
    """Generate section for output mismatches."""
    if not mismatches:
        return '<div class="action-section"><p>No output mismatches!</p></div>'

    # Show ALL mismatches with full paths
    items = []
    for path, expected, actual in sorted(mismatches, key=lambda x: x[0]):
        full_path = f"programs/{path}"
        diff_html = _generate_unified_diff(expected, actual)
        items.append(f"""
        <details>
            <summary><code>{html.escape(full_path)}</code></summary>
            <div class="detail-content">
                {diff_html}
            </div>
        </details>
        """)

    return f'<div class="action-section">{chr(10).join(items)}</div>'


def generate_markdown_report(
    run: dict,
    by_status: dict,
    reference_errors: dict,
    type_errors: dict,
    syntax_errors: dict,
    compile_errors: dict,
    output_mismatches: list,
    filter_pattern: str | None = None,
) -> str:
    """Generate a Markdown report."""
    lines = []

    total = run.get("total_programs", 0)
    passed = len(by_status.get(Status.RUNTIME_PASS, []))
    failed = len(by_status.get(Status.RUNTIME_FAIL, []))
    errors = len(by_status.get(Status.RUNTIME_ERROR, []))
    compile_fail = len(by_status.get(Status.COMPILE_FAIL, []))
    pass_rate = (100 * passed / total) if total > 0 else 0

    # Header
    lines.append(f"# Prescrypt Test Report - Run #{run.get('id')}")
    lines.append("")
    lines.append(
        f"**Branch:** {run.get('git_branch', 'unknown')} @ {run.get('git_commit', 'unknown')[:8] if run.get('git_commit') else 'unknown'}"
    )
    lines.append(f"**Date:** {run.get('started_at', 'unknown')}")
    if filter_pattern:
        lines.append(f"**Filter:** `{filter_pattern}`")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Count | Percentage |")
    lines.append("|--------|-------|------------|")
    lines.append(f"| Total Tests | {total} | 100% |")
    lines.append(f"| Passing | {passed} | {pass_rate:.1f}% |")
    lines.append(
        f"| Output Mismatch | {failed} | {100 * failed / total if total else 0:.1f}% |"
    )
    lines.append(
        f"| Runtime Error | {errors} | {100 * errors / total if total else 0:.1f}% |"
    )
    lines.append(
        f"| Compile Fail | {compile_fail} | {100 * compile_fail / total if total else 0:.1f}% |"
    )
    lines.append("")

    # Helper to check if item matches filter
    def matches_filter(text: str) -> bool:
        if not filter_pattern:
            return True
        try:
            return bool(re.search(filter_pattern, text, re.IGNORECASE))
        except re.error:
            return filter_pattern.lower() in text.lower()

    # Missing Names (Reference Errors)
    filtered_ref_errors = {
        name: paths
        for name, paths in reference_errors.items()
        if name != "_other_" and matches_filter(name)
    }
    if filtered_ref_errors:
        lines.append("## Missing Names (ReferenceError)")
        lines.append("")
        for name, paths in sorted(
            filtered_ref_errors.items(), key=lambda x: -len(x[1])
        ):
            lines.append(f"### `{name}` ({len(paths)} tests)")
            lines.append("")
            for path in sorted(paths):
                lines.append(f"- `programs/{path}`")
            lines.append("")

    # Compile Errors
    filtered_compile = {
        err_type: items
        for err_type, items in compile_errors.items()
        if any(
            matches_filter(err_type) or matches_filter(path) or matches_filter(msg)
            for path, msg in items
        )
    }
    if filtered_compile:
        lines.append("## Compilation Errors")
        lines.append("")
        for err_type, items in sorted(
            filtered_compile.items(), key=lambda x: -len(x[1])
        ):
            # Filter items within this error type
            filtered_items = [
                (path, msg)
                for path, msg in items
                if matches_filter(err_type)
                or matches_filter(path)
                or matches_filter(msg)
            ]
            if not filtered_items:
                continue
            lines.append(f"### {err_type} ({len(filtered_items)} programs)")
            lines.append("")
            for path, msg in sorted(filtered_items, key=lambda x: x[0]):
                lines.append(f"#### `programs/{path}`")
                lines.append("")
                lines.append("```")
                lines.append(msg)
                lines.append("```")
                lines.append("")

    # Type Errors
    filtered_type = {
        err_type: items
        for err_type, items in type_errors.items()
        if any(
            matches_filter(err_type) or matches_filter(path) or matches_filter(msg)
            for path, msg in items
        )
    }
    if filtered_type:
        lines.append("## Type Errors")
        lines.append("")
        for err_type, items in sorted(filtered_type.items(), key=lambda x: -len(x[1])):
            filtered_items = [
                (path, msg)
                for path, msg in items
                if matches_filter(err_type)
                or matches_filter(path)
                or matches_filter(msg)
            ]
            if not filtered_items:
                continue
            lines.append(f"### {err_type} ({len(filtered_items)} programs)")
            lines.append("")
            for path, msg in sorted(filtered_items, key=lambda x: x[0]):
                lines.append(f"#### `programs/{path}`")
                lines.append("")
                lines.append("```")
                lines.append(msg)
                lines.append("```")
                lines.append("")

    # Syntax Errors
    filtered_syntax = {
        err_type: items
        for err_type, items in syntax_errors.items()
        if any(
            matches_filter(err_type) or matches_filter(path) or matches_filter(msg)
            for path, msg in items
        )
    }
    if filtered_syntax:
        lines.append("## Syntax Errors")
        lines.append("")
        for err_type, items in sorted(
            filtered_syntax.items(), key=lambda x: -len(x[1])
        ):
            filtered_items = [
                (path, msg)
                for path, msg in items
                if matches_filter(err_type)
                or matches_filter(path)
                or matches_filter(msg)
            ]
            if not filtered_items:
                continue
            lines.append(f"### {err_type} ({len(filtered_items)} programs)")
            lines.append("")
            for path, msg in sorted(filtered_items, key=lambda x: x[0]):
                lines.append(f"#### `programs/{path}`")
                lines.append("")
                lines.append("```")
                lines.append(msg)
                lines.append("```")
                lines.append("")

    # Output Mismatches
    filtered_mismatches = [
        (path, expected, actual)
        for path, expected, actual in output_mismatches
        if matches_filter(path) or matches_filter(expected) or matches_filter(actual)
    ]
    if filtered_mismatches:
        lines.append(f"## Output Mismatches ({len(filtered_mismatches)} tests)")
        lines.append("")
        for path, expected, actual in sorted(filtered_mismatches, key=lambda x: x[0]):
            lines.append(f"### `programs/{path}`")
            lines.append("")
            # Generate unified diff
            expected_lines = expected.splitlines(keepends=True)
            actual_lines = actual.splitlines(keepends=True)
            diff = list(
                difflib.unified_diff(
                    expected_lines,
                    actual_lines,
                    fromfile="expected (Python)",
                    tofile="actual (JavaScript)",
                    lineterm="",
                )
            )
            if diff:
                lines.append("```diff")
                for line in diff:
                    lines.append(line.rstrip("\n"))
                lines.append("```")
            else:
                lines.append("**Expected (Python):**")
                lines.append("```")
                lines.append(expected or "(empty)")
                lines.append("```")
                lines.append("")
                lines.append("**Actual (JavaScript):**")
                lines.append("```")
                lines.append(actual or "(empty)")
                lines.append("```")
            lines.append("")

    return "\n".join(lines)


def categorize_results(results: list) -> tuple[dict, dict, dict, dict, list]:
    """Categorize test results into error types.

    Args:
        results: List of result rows from database

    Returns:
        Tuple of (reference_errors, type_errors, syntax_errors, compile_errors, output_mismatches)
    """
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
            # Skip line:column: prefix (e.g., "3:22: error: ...")
            err_type = "other"

            # Try to extract the actual error message after "error:"
            if "error:" in error_msg.lower():
                # Find the position after "error:" and extract what follows
                idx = error_msg.lower().find("error:")
                err_text = error_msg[idx + 6:].strip()
                # Take the first meaningful phrase as error type
                if err_text:
                    # Truncate at reasonable length for grouping
                    err_type = err_text[:60].strip()
                    if len(err_text) > 60:
                        err_type += "..."
            elif "gen_expr not implemented" in error_msg:
                match = re.search(r"gen_expr not implemented for <(\w+)", error_msg)
                err_type = (
                    f"gen_expr not implemented: {match.group(1)}"
                    if match
                    else "gen_expr not implemented"
                )
            elif "gen_stmt not implemented" in error_msg:
                match = re.search(r"gen_stmt not implemented for <(\w+)", error_msg)
                err_type = (
                    f"gen_stmt not implemented: {match.group(1)}"
                    if match
                    else "gen_stmt not implemented"
                )
            elif ":" in error_msg:
                # Skip leading line:col: patterns
                parts = error_msg.split(":")
                for part in parts:
                    stripped = part.strip()
                    # Skip if it's a number (line/col) or empty
                    if stripped and not stripped.isdigit():
                        err_type = stripped[:60]
                        break

            compile_errors[err_type].append((path, error_msg))

        elif r["status"] == Status.RUNTIME_FAIL:
            expected = (r["cpython_output"] or "").strip()
            actual = (r["js_output"] or "").strip()
            output_mismatches.append((path, expected[:200], actual[:200]))

    return reference_errors, type_errors, syntax_errors, compile_errors, output_mismatches
