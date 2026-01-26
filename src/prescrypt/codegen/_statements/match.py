"""Code generation for match statements (Python 3.10+)."""

from __future__ import annotations

import re

from prescrypt.codegen.main import CodeGen, gen_stmt
from prescrypt.codegen.utils import flatten
from prescrypt.exceptions import JSError
from prescrypt.front import ast


@gen_stmt.register
def gen_match(node: ast.Match, codegen: CodeGen) -> list[str]:
    """Generate JavaScript code for a match statement.

    Generates a series of if/else if statements that test patterns.

    Supports:
    - MatchValue: literal values (case 0:)
    - MatchSingleton: None, True, False
    - MatchOr: alternatives (case 1 | 2:)
    - MatchAs: capture/wildcard (case n: or case _:)
    - MatchSequence: sequences (case [a, b]:)
    - MatchStar: starred patterns (case [first, *rest]:)
    - MatchMapping: dictionaries (case {"x": x}:)
    - MatchClass: class instances (case Point(x=x):)
    - Guards: (case n if n > 0:)
    """
    code = []

    # Collect all variable names that will be assigned in the match
    # These need to be declared before the if/else chain for proper scoping
    match_vars: set[str] = set()
    for case in node.cases:
        _collect_pattern_names_set(case.pattern, match_vars)
        _collect_body_names_set(case.body, match_vars)

    # Declare collected variables (those not already known)
    for var_name in sorted(match_vars):
        if not codegen.ns.is_known(var_name):
            codegen.add_var(var_name)
            code.append(f"let {var_name};")

    # Generate subject expression once and store in temp variable
    subject_js = flatten(codegen.gen_expr(node.subject))
    subject_var = codegen.dummy("match_subject")
    code.append(f"let {subject_var} = {subject_js};")

    # Generate if/else chain for cases
    first = True
    for case in node.cases:
        condition, bindings = _gen_pattern_condition(case.pattern, subject_var, codegen)

        # Add guard if present
        if case.guard is not None:
            # For guards, we need to substitute pattern-bound names with subject
            # e.g., `case n if n > 0:` should use subject_var, not n
            guard_substitutions = _get_pattern_substitutions(case.pattern, subject_var)
            guard_js = flatten(codegen.gen_expr(case.guard))
            # Apply substitutions
            for var_name, replacement in guard_substitutions.items():
                # Simple word-boundary replacement
                guard_js = re.sub(rf"\b{var_name}\b", replacement, guard_js)
            if condition:
                condition = f"({condition}) && ({guard_js})"
            else:
                condition = guard_js

        # Generate the if/else if clause
        if first:
            code.append(f"if ({condition}) {{")
            first = False
        elif condition:
            code.append(f"}} else if ({condition}) {{")
        else:
            # Wildcard case - always matches
            code.append("} else {")

        # Add bindings inside the block
        for binding in bindings:
            code.append(f"  {binding}")

        # Generate body
        for stmt in case.body:
            body_code = codegen.gen_stmt(stmt)
            if isinstance(body_code, list):
                for line in body_code:
                    code.append(f"  {line}")
            else:
                code.append(f"  {body_code}")

    code.append("}")

    return code


def _gen_pattern_condition(
    pattern: ast.pattern, subject: str, codegen: CodeGen
) -> tuple[str, list[str]]:
    """Generate a condition expression for a pattern.

    Returns:
        Tuple of (condition_js, bindings) where:
        - condition_js: JavaScript condition expression (empty string for wildcard)
        - bindings: List of variable binding statements
    """
    match pattern:
        case ast.MatchValue(value=value):
            # Literal value: case 0:
            value_js = flatten(codegen.gen_expr(value))
            return f"{codegen.call_std_function('op_equals', [subject, value_js])}", []

        case ast.MatchSingleton(value=value):
            # None, True, False
            if value is None:
                return f"({subject} === null)", []
            elif value is True:
                return f"({subject} === true)", []
            elif value is False:
                return f"({subject} === false)", []
            else:
                msg = f"Unsupported singleton value: {value}"
                raise JSError(msg, pattern)

        case ast.MatchAs(pattern=None, name=None):
            # Wildcard: case _:
            return "", []

        case ast.MatchAs(pattern=None, name=name):
            # Capture without pattern: case n:
            # Variable already registered by _collect_pattern_names
            return "", [f"{name} = {subject};"]

        case ast.MatchAs(pattern=inner_pattern, name=name):
            # Pattern with capture: case [a, b] as pair:
            inner_cond, inner_bindings = _gen_pattern_condition(
                inner_pattern, subject, codegen
            )
            if name:
                # Variable already registered by _collect_pattern_names
                inner_bindings.append(f"{name} = {subject};")
            return inner_cond, inner_bindings

        case ast.MatchOr(patterns=patterns):
            # Alternative patterns: case 1 | 2:
            conditions = []
            # OR patterns can't have bindings (they must match the same names)
            for p in patterns:
                cond, _ = _gen_pattern_condition(p, subject, codegen)
                if cond:
                    conditions.append(cond)
            if conditions:
                return "(" + " || ".join(conditions) + ")", []
            return "", []

        case ast.MatchSequence(patterns=patterns):
            # Sequence pattern: case [a, b]:
            return _gen_sequence_pattern(patterns, subject, codegen)

        case ast.MatchMapping(keys=keys, patterns=patterns, rest=rest):
            # Dictionary pattern: case {"x": x, "y": y}:
            return _gen_mapping_pattern(keys, patterns, rest, subject, codegen)

        case ast.MatchClass(
            cls=cls,
            patterns=pos_patterns,
            kwd_attrs=kwd_attrs,
            kwd_patterns=kwd_patterns,
        ):
            # Class pattern: case Point(x=0, y=y):
            return _gen_class_pattern(
                cls, pos_patterns, kwd_attrs, kwd_patterns, subject, codegen
            )

        case ast.MatchStar(name=name):
            # Star patterns are handled inside _gen_sequence_pattern
            # If we get here, it's a star outside a sequence which is invalid
            msg = "Star pattern (*) can only appear inside sequence patterns"
            raise JSError(msg, pattern)

        case _:
            msg = f"Unsupported match pattern type: {type(pattern).__name__}"
            raise JSError(msg, pattern)


def _collect_pattern_names_set(pattern: ast.pattern, names: set[str]) -> None:
    """Collect variable names from a pattern into a set."""
    match pattern:
        case ast.MatchAs(name=name) if name is not None:
            names.add(name)
            if hasattr(pattern, "pattern") and pattern.pattern is not None:
                _collect_pattern_names_set(pattern.pattern, names)

        case ast.MatchOr(patterns=patterns):
            for p in patterns:
                _collect_pattern_names_set(p, names)

        case ast.MatchSequence(patterns=patterns):
            for p in patterns:
                _collect_pattern_names_set(p, names)

        case ast.MatchStar(name=name):
            if name is not None:
                names.add(name)

        case ast.MatchMapping(patterns=patterns, rest=rest):
            for p in patterns:
                _collect_pattern_names_set(p, names)
            if rest is not None:
                names.add(rest)

        case ast.MatchClass(patterns=pos_patterns, kwd_patterns=kwd_patterns):
            for p in pos_patterns:
                _collect_pattern_names_set(p, names)
            for p in kwd_patterns:
                _collect_pattern_names_set(p, names)

        case _:
            pass


def _collect_body_names_set(body: list[ast.stmt], names: set[str]) -> None:
    """Collect variable names assigned in a body into a set.

    This is a simplified version - only handles direct assignments.
    """
    for stmt in body:
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
        elif isinstance(stmt, ast.AnnAssign):
            if isinstance(stmt.target, ast.Name):
                names.add(stmt.target.id)


def _get_pattern_substitutions(pattern: ast.pattern, subject: str) -> dict[str, str]:
    """Get variable name -> subject substitutions for guards.

    For `case n if n > 0:`, returns {n: subject_var} so the guard
    can use the subject variable instead of the not-yet-bound n.
    """
    subs: dict[str, str] = {}

    match pattern:
        case ast.MatchAs(pattern=None, name=name) if name is not None:
            # Simple capture: case n:
            subs[name] = subject

        case ast.MatchAs(pattern=inner, name=name):
            # Pattern with capture: case [a, b] as pair:
            if name:
                subs[name] = subject
            if inner:
                # For inner patterns, need element access
                # This is complex, skip for now
                pass

        case ast.MatchSequence(patterns=patterns):
            # For sequence patterns, map element names to subject[i]
            for i, p in enumerate(patterns):
                if isinstance(p, ast.MatchAs) and p.pattern is None and p.name:
                    subs[p.name] = f"{subject}[{i}]"

        case ast.MatchMapping(keys=keys, patterns=patterns):
            # For mapping patterns, map captured names to subject[key]
            from prescrypt.codegen.utils import flatten as _flatten

            for key, p in zip(keys, patterns):
                if isinstance(p, ast.MatchAs) and p.pattern is None and p.name:
                    # Note: We can't easily get the codegen here, so use simple key access
                    if isinstance(key, ast.Constant):
                        if isinstance(key.value, str):
                            subs[p.name] = f'{subject}["{key.value}"]'
                        else:
                            subs[p.name] = f"{subject}[{key.value}]"

        case ast.MatchClass(kwd_attrs=kwd_attrs, kwd_patterns=kwd_patterns):
            # For class patterns, map captured names to subject.attr
            for attr, p in zip(kwd_attrs, kwd_patterns):
                if isinstance(p, ast.MatchAs) and p.pattern is None and p.name:
                    subs[p.name] = f"{subject}.{attr}"

        case _:
            pass

    return subs


def _gen_sequence_pattern(
    patterns: list[ast.pattern], subject: str, codegen: CodeGen
) -> tuple[str, list[str]]:
    """Generate condition and bindings for a sequence pattern.

    Handles:
    - case [a, b, c]: - fixed length
    - case [first, *rest]: - starred at end
    - case [*rest, last]: - starred at start
    - case [first, *middle, last]: - starred in middle
    """
    conditions = []
    bindings = []

    # Check it's an array
    conditions.append(f"Array.isArray({subject})")

    # Find star pattern position (if any)
    star_index = None
    star_name = None
    for i, p in enumerate(patterns):
        if isinstance(p, ast.MatchStar):
            star_index = i
            star_name = p.name  # Can be None for case [a, *_, b]
            break

    if star_index is None:
        # No star - exact length match
        conditions.append(f"{subject}.length === {len(patterns)}")
        _gen_sequence_elements(patterns, subject, 0, codegen, conditions, bindings)
    else:
        # Star pattern - minimum length check
        before_star = patterns[:star_index]
        after_star = patterns[star_index + 1 :]
        min_length = len(before_star) + len(after_star)

        if min_length > 0:
            conditions.append(f"{subject}.length >= {min_length}")
        # else: no minimum needed, empty array matches [*rest]

        # Handle elements before star (positive indices)
        _gen_sequence_elements(before_star, subject, 0, codegen, conditions, bindings)

        # Handle elements after star (negative indices from end)
        if after_star:
            for i, p in enumerate(after_star):
                # Use negative index: subject[subject.length - (len(after_star) - i)]
                offset = len(after_star) - i
                elem_access = f"{subject}[{subject}.length - {offset}]"
                _gen_single_sequence_element(
                    p, elem_access, codegen, conditions, bindings
                )

        # Handle star capture
        if star_name is not None:
            # slice(start, end) where end is length - after_count
            if after_star:
                bindings.append(
                    f"{star_name} = {subject}.slice({star_index}, {subject}.length - {len(after_star)});"
                )
            else:
                bindings.append(f"{star_name} = {subject}.slice({star_index});")

    return " && ".join(conditions), bindings


def _gen_sequence_elements(
    patterns: list[ast.pattern],
    subject: str,
    start_index: int,
    codegen: CodeGen,
    conditions: list[str],
    bindings: list[str],
) -> None:
    """Generate conditions and bindings for a list of sequence elements."""
    for i, p in enumerate(patterns):
        elem_access = f"{subject}[{start_index + i}]"
        _gen_single_sequence_element(p, elem_access, codegen, conditions, bindings)


def _gen_single_sequence_element(
    p: ast.pattern,
    elem_access: str,
    codegen: CodeGen,
    conditions: list[str],
    bindings: list[str],
) -> None:
    """Generate condition and binding for a single sequence element."""
    match p:
        case ast.MatchAs(pattern=None, name=None):
            # Wildcard element: [_, b]
            pass

        case ast.MatchAs(pattern=None, name=name):
            # Capture element: [a, b]
            bindings.append(f"{name} = {elem_access};")

        case ast.MatchValue(value=value):
            # Literal element: [1, b]
            value_js = flatten(codegen.gen_expr(value))
            conditions.append(
                f"{codegen.call_std_function('op_equals', [elem_access, value_js])}"
            )

        case ast.MatchOr(patterns=or_patterns):
            # OR pattern in element: [1 | 2, b]
            or_conds = []
            for op in or_patterns:
                oc, _ = _gen_pattern_condition(op, elem_access, codegen)
                if oc:
                    or_conds.append(oc)
            if or_conds:
                conditions.append("(" + " || ".join(or_conds) + ")")

        case ast.MatchSequence(patterns=nested_patterns):
            # Nested sequence: [[a, b], c]
            nested_cond, nested_bindings = _gen_sequence_pattern(
                nested_patterns, elem_access, codegen
            )
            if nested_cond:
                conditions.append(nested_cond)
            bindings.extend(nested_bindings)

        case _:
            # Recurse for other patterns
            elem_cond, elem_bindings = _gen_pattern_condition(p, elem_access, codegen)
            if elem_cond:
                conditions.append(elem_cond)
            bindings.extend(elem_bindings)


def _gen_mapping_pattern(
    keys: list[ast.expr],
    patterns: list[ast.pattern],
    rest: str | None,
    subject: str,
    codegen: CodeGen,
) -> tuple[str, list[str]]:
    """Generate condition and bindings for a mapping pattern.

    Handles: case {"x": x, "y": y}:, case {"type": "point", **rest}:
    """
    conditions = []
    bindings = []

    # Check it's an object (not null, not array)
    conditions.append(f"(typeof {subject} === 'object' && {subject} !== null)")
    conditions.append(f"!Array.isArray({subject})")

    # Check each key exists and matches pattern
    for key, pattern in zip(keys, patterns):
        key_js = flatten(codegen.gen_expr(key))
        key_access = f"{subject}[{key_js}]"

        # Check key exists
        conditions.append(f"({key_js} in {subject})")

        match pattern:
            case ast.MatchAs(pattern=None, name=None):
                # Wildcard: {"x": _}
                pass

            case ast.MatchAs(pattern=None, name=name):
                # Capture: {"x": x}
                bindings.append(f"{name} = {key_access};")

            case ast.MatchValue(value=value):
                # Literal: {"type": "point"}
                value_js = flatten(codegen.gen_expr(value))
                conditions.append(
                    f"{codegen.call_std_function('op_equals', [key_access, value_js])}"
                )

            case _:
                # Recurse for nested patterns
                elem_cond, elem_bindings = _gen_pattern_condition(
                    pattern, key_access, codegen
                )
                if elem_cond:
                    conditions.append(elem_cond)
                bindings.extend(elem_bindings)

    # Handle **rest capture
    if rest is not None:
        # Collect remaining keys into a new object
        key_exprs = [flatten(codegen.gen_expr(k)) for k in keys]
        exclude_set = "{" + ", ".join(key_exprs) + "}"
        bindings.append(
            f"{rest} = Object.fromEntries("
            f"Object.entries({subject}).filter(([k]) => !{exclude_set}.has(k)));"
        )

    return " && ".join(conditions), bindings


def _gen_class_pattern(
    cls: ast.expr,
    pos_patterns: list[ast.pattern],
    kwd_attrs: list[str],
    kwd_patterns: list[ast.pattern],
    subject: str,
    codegen: CodeGen,
) -> tuple[str, list[str]]:
    """Generate condition and bindings for a class pattern.

    Handles: case Point(x=0, y=y):
    """
    conditions = []
    bindings = []

    # Get class name for isinstance check
    cls_js = flatten(codegen.gen_expr(cls))

    # Check it's an instance of the class
    conditions.append(f"({subject} instanceof {cls_js})")

    # Handle positional patterns using __match_args__
    if pos_patterns:
        # Positional patterns require __match_args__ on the class
        # For now, we'll use __match_args__ if defined, otherwise error
        # Common case: Point(x, y) where Point.__match_args__ = ('x', 'y')
        for i, pattern in enumerate(pos_patterns):
            # Access attribute via __match_args__
            attr_access = f"{subject}[{cls_js}.__match_args__[{i}]]"

            match pattern:
                case ast.MatchAs(pattern=None, name=None):
                    # Wildcard
                    pass

                case ast.MatchAs(pattern=None, name=name):
                    # Capture
                    bindings.append(f"{name} = {attr_access};")

                case ast.MatchValue(value=value):
                    # Literal
                    value_js = flatten(codegen.gen_expr(value))
                    conditions.append(
                        f"{codegen.call_std_function('op_equals', [attr_access, value_js])}"
                    )

                case _:
                    # Recurse
                    elem_cond, elem_bindings = _gen_pattern_condition(
                        pattern, attr_access, codegen
                    )
                    if elem_cond:
                        conditions.append(elem_cond)
                    bindings.extend(elem_bindings)

    # Handle keyword patterns
    for attr, pattern in zip(kwd_attrs, kwd_patterns):
        attr_access = f"{subject}.{attr}"

        match pattern:
            case ast.MatchAs(pattern=None, name=None):
                # Wildcard
                pass

            case ast.MatchAs(pattern=None, name=name):
                # Capture
                bindings.append(f"{name} = {attr_access};")

            case ast.MatchValue(value=value):
                # Literal: Point(x=0)
                value_js = flatten(codegen.gen_expr(value))
                conditions.append(
                    f"{codegen.call_std_function('op_equals', [attr_access, value_js])}"
                )

            case _:
                # Recurse
                elem_cond, elem_bindings = _gen_pattern_condition(
                    pattern, attr_access, codegen
                )
                if elem_cond:
                    conditions.append(elem_cond)
                bindings.extend(elem_bindings)

    return " && ".join(conditions), bindings
