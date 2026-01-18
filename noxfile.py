from __future__ import annotations

import nox

PYTHONS = ["3.10", "3.11", "3.12", "3.13", "3.14"]


@nox.session(python=PYTHONS)
def tests(session: nox.Session):
    uv_sync(session)
    session.run("pytest")


@nox.session(python=PYTHONS[0])
def lint(session: nox.Session):
    uv_sync(session)
    session.run("ruff", "check")


#
# Utils
#
def uv_sync(session: nox.Session):
    session.run(
        "uv", "sync", "-q", "--all-groups", "--all-extras", "--active", external=True
    )
