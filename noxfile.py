from __future__ import annotations

import nox

PYTHONS = ["3.10", "3.11", "3.12", "3.13", "3.14"]
# nox.options.sessions = ["lint", "pytest"]


@nox.session(python=PYTHONS)
def tests(session: nox.Session):
    # Note: we use 'uv' instead of 'pip' to make setup quicker
    # '--active' and 'external=True' are needed for proper setup
    session.run("uv", "sync", "--active", external=True)
    session.run("uv", "run", "--active", "pytest", external=True)


@nox.session(python=PYTHONS[0])
def lint(session: nox.Session):
    # Note: we use 'uv' instead of 'pip' to make setup quicker
    # '--active' and 'external=True' are needed for proper setup
    session.run("uv", "sync", "--active", external=True)
    session.run("uv", "run", "--active", "ruff", "check", external=True)
